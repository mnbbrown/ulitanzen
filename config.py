import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://dev:dev@localhost/ulitanzen')
SQLALCHEMY_ECHO = True