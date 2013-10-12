from flask.ext.sqlalchemy import SQLAlchemy
import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), '..'))
from app import app
db = SQLAlchemy(app)
db_session = db.session

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    db.Model.metadata.create_all()