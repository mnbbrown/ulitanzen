import sys,os

try:
    import redis
except Exception as e:
    print e
    sys.exit(2)

class Service:

    name = ""
    status = False
    status_str = ""
    message = ""

    def __init__(self, name, status=False, message=""):
        self.name = name
        self.status = status
        if status is False:
            self.status_str = "ERROR"
        if status:
            self.status_str = "RUNNING"
        self.message = message

def check_redis(host='localhost', port=6379, password=None, default_timeout=300):
    db = ''
    info_cmd = ''
    perfout = '|'
    if host:
        try:
            db = redis.Redis(host="%s" % (host), port=int(port), socket_timeout=int(default_timeout))
        except Exception as e:
            return Service("Redis", False, 'CRITICAL %s' % (e))
        try:
            info_cmd = db.info()
        except Exception as e:
            return Service("Redis", False, 'CRITICAL %s' % (e))
        for key in info_cmd.keys():
            ktype = type(info_cmd[key])
            if ktype is int:
                perfout = perfout + ' %s=%d'% (key, info_cmd[key])
            elif ktype is float:
                perfout = perfout + ' %s=%f' % (key, info_cmd[key])
            elif ktype is dict:
                for k, v in info_cmd[key].items():
                    if type(v) is int:
                        perfout = perfout + ' %s_%s=%d'% (key, k, v)
                    elif type(v) is float:
                        perfout = perfout + ' %s_%s=%f' % (key, k, v)

        if info_cmd['role'] == 'master':
            return Service("Redis", True, 'OK Master Redis Server %s is Running %s %s' % ( host, info_cmd['redis_version'], perfout ))

        elif info_cmd['role'] == 'slave':
            if info_cmd['master_link_status'] == 'up' and info_cmd['master_sync_in_progress'] == 0:
                return Service("Redis", True, 'OK Master %s is up and Slave %s is in sync %s' % ( info_cmd['master_host'], host, perfout ))
            elif info_cmd['master_link_status'] == 'up' and info_cmd['master_sync_in_progress'] == 1:
                return Service("Redis", True, 'WARNING Master %s is up and Slave %s is out of sync %s' % ( info_cmd['master_host'], host, perfout ))
            elif info_cmd['master_link_status'] == 'down':
                return Service("Redis", True, 'CRITICAL Master %s is down and Slave %s is out of sync %s' % ( info_cmd['master_host'], host, perfout ))
    else:
        print 'You did not either pass the redis server or redis password'

def check_postgres():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.exc import OperationalError

    some_engine = create_engine(os.environ.get('DATABASE_URL','postgresql://dev:dev@localhost/ulitanzen'))
    Session = sessionmaker(bind=some_engine)
    session = Session()
    try:
        session.execute("SELECT * FROM guests")
    except OperationalError, e:
        return Service("PostgreSQL", False, message=str(e))
    return Service("PostgreSQL", True)


