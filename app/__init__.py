from flask import Flask, request, current_app,render_template
from flask.ext.sqlalchemy import SQLAlchemy, DeclarativeMeta
from json import JSONEncoder, dumps
import os
from werkzeug.contrib.cache import RedisCache
from subprocess import call

db = SQLAlchemy()

cache = RedisCache()

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

def new_alchemy_encoder(revisit_self = False, fields_to_expand = []):
	_visited_objs = []
	class AlchemyEncoder(JSONEncoder):
		def default(self, obj):
			if isinstance(obj.__class__, DeclarativeMeta):
				# don't re-visit self
				if revisit_self:
					if obj in _visited_objs:
						return "READ"
					_visited_objs.append(obj)

				# go through each field in this SQLalchemy class
				fields = {}
				for field in obj.__mapper__.iterate_properties:
					val = getattr(obj, field.key)
					# is this field another SQLalchemy object, or a list of SQLalchemy objects?
					if isinstance(val.__class__, DeclarativeMeta) or (isinstance(val, list) and len(val) > 0 and isinstance(val[0].__class__, DeclarativeMeta)):
						# unless we're expanding this field, stop here
						if field.key not in fields_to_expand:
							# not expanding this field: set it to None and continue
							fields[field.key] = None
							continue

					fields[field.key] = val
				# a json-encodable dict
				return fields
			return JSONEncoder.default(self, obj)
	return AlchemyEncoder

def jsonify(*args):
	return current_app.response_class(dumps(*args, indent=2, cls=new_alchemy_encoder(), check_circular=False), mimetype='application/json')

def invalidateCache(identifier):
	print "Invalidating Cache!!"
	cache.delete(identifier)

class Seat(db.Model):
	__tablename__ = 'seats'

	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	table_number = db.Column(db.Integer)
	guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'))

	def book(self, guest=None):
		guest.seats_booked = guest.seats_booked - 1;
		self.guest_id = request.form.get('guest_id',None)
		db.session.add(self)
		db.session.add(guest)
		db.session.commit()

	def unbook(self):
		if self.guest_id is not None:
			current_guest = Guest.query.get_or_404(self.guest_id)
			current_guest.seats_booked = current_guest.seats_booked + 1;
			self.guest_id = None
			db.session.add(current_guest)
			db.session.add(self)
			db.session.commit()




class Guest(db.Model):
	__tablename__ = 'guests'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	email = db.Column(db.String)
	seats_booked = db.Column(db.Integer)
	paid = db.Column(db.Boolean)

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/api/seats',methods=["GET"])
def list_seats():
	cacheId = "seats/list"
	seats = cache.get(cacheId)
	if seats is None:
		print "Calling DB"
		seats = Seat.query.all()
		cache.set(cacheId, seats, timeout=60*5)
	return jsonify(seats)

@app.route('/api/guests/<int:id>/seats')
def get_guest_seats(id):
	seats = Seat.query.filter_by(guest_id=id).all()
	return jsonify(seats)

@app.route('/api/guests/<int:id>/seats', methods=['DELETE'])
def unbook_guest_seats(id):
	seats = Seat.query.filter_by(guest_id=id).all()
	for seat in seats:
		seat.unbook()
	return jsonify(200)


@app.route('/api/seats/<int:id>', methods=["PUT"])
def update_seat(id):
	invalidateCache("seats/list")
	invalidateCache("guests/list")
	seat = Seat.query.get_or_404(id)
	new_guest_id = request.form.get('guest_id')
	if new_guest_id is None and seat.guest_id is not None:
		seat.unbook()
	elif new_guest_id is not None and seat.guest_id is None:
		guest = Guest.query.get_or_404(new_guest_id)
		seat.book(guest)
	return jsonify(seat)

@app.route('/api/seats/<int:id>', methods=['GET'])
def get_seat(id):
	seat = Seat.query.get_or_404(id)
	return jsonify(seat)

@app.route('/api/guests', methods=['GET'])
def list_guests():
	cacheId = "guests/list"
	guests = cache.get(cacheId)
	if guests is None:
		print "Calling DB"
		guests = Guest.query.all()
		cache.set(cacheId, guests, timeout=60*5)
	return jsonify(guests)

@app.route('/api/guests/<int:id>', methods=['GET'])
def get_guest(id):
	guest = Guest.query.get_or_404(id)
	return jsonify(guest)

@app.route('/api/status', methods=['GET'])
def app_status():
	import check
	services = []
	services.append(check.check_redis())
	services.append(check.check_postgres())
	return render_template('status.html', services=services)


def setup_db(tables=0, seats_per_table=0):
	from sqlalchemy import create_engine
	from sqlalchemy.orm import sessionmaker

	some_engine = create_engine(os.environ.get('DATABASE_URL','postgresql://dev:dev@localhost/ulitanzen'))
	Session = sessionmaker(bind=some_engine)
	session = Session()
	for tn in range(0,tables):
		for sn in range(0, seats_per_table):
			query = "INSERT INTO seats (number, table_number) VALUES ({0}, {1})".format(sn+1,tn+1)
			session.execute(query)
	session.commit()