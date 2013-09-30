from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), '..'))
import config

engine = create_engine(config.SQLALCHEMY_DATABASE_URI, encoding='utf8', echo=False, connect_args = {'charset' : 'utf8'})
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
db_query = Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)