import logging
from flask import Flask, request, send_from_directory
from flask_appbuilder import SQLA, AppBuilder
from flask_cors import CORS
import ctypes
import logging
from sqlalchemy.engine import Engine
from sqlalchemy import event



app = Flask(__name__, static_url_path='')
app.config.from_object('config')
app.config['PROPAGATE_EXCEPTIONS'] = True
CORS(app)
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
  

from app import views, models


