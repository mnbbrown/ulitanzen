from flask import Flask, request, current_app,render_template
from flask.ext.sqlalchemy import SQLAlchemy, DeclarativeMeta
from json import JSONEncoder, dumps

db = SQLAlchemy()

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

class Seat(db.Model):
	__tablename__ = 'seats'

	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	table_number = db.Column(db.Integer)
	guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'))

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
	seats = Seat.query.all()
	return jsonify(seats)

@app.route('/api/guests/<int:id>/seats')
def get_guest_seats(id):
	seats = Seat.query.filter_by(guest_id=id).all()
	return jsonify(seats)

@app.route('/api/seats/<int:id>', methods=["PUT"])
def update_seat(id):
	guest = Guest.query.get_or_404(request.form.get('guest_id',None))
	guest.seats_booked = guest.seats_booked - 1;
	seat = Seat.query.get_or_404(id)
	seat.guest_id = request.form.get('guest_id',None)
	db.session.add(guest)
	db.session.add(seat)
	db.session.commit()
	return jsonify(seat)

@app.route('/api/guests', methods=['GET'])
def list_guests():
	guests = Guest.query.all()
	return jsonify(guests)

@app.route('/api/guests/<int:id>', methods=['GET'])
def get_guest(id):
	guest = Guest.query.get_or_404(id)
	return jsonify(guest)


def setup_db(tables=0, seats_per_table=0):
	import psycopg2
	conn = psycopg2.connect("dbname=ulitanzen user=dev password=dev")
	cur = conn.cursor()
	for tn in range(0,tables):
		for sn in range(0, seats_per_table):
			cur.execute("INSERT INTO seats (number, table_number) VALUES (%s, %s)",(sn+1,tn+1))
	conn.commit()
	cur.close()
	conn.close()