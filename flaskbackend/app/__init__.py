import logging
from flask import Flask, request, send_from_directory
from flask_appbuilder import SQLA, AppBuilder
from flask_cors import CORS
"""
 Logging configuration
"""






logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__, static_url_path='')

logging.basicConfig(level=logging.INFO)


logging.getLogger('flask_cors').level = logging.DEBUG

CORS(app)
app.config.from_object('config')


db = SQLA(app)
appbuilder = AppBuilder(app, db.session)





"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""    

from app import views

