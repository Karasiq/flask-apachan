import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'db'))
import models, database
from database import db_session
from sqlalchemy import func

def clean():
    users = db_session.query(models.User).filter_by(last_post = None)
    for u in users:
        print('User %d deleted' % u.id)
        db_session.delete(u)
    posts = db_session.query(models.Post).filter_by(parent = 0, answers = 0)
    for p in posts:
        print('Post %d deleted' % p.id)
        db_session.delete(p)
    db_session.commit()

if __name__ == '__main__':
    clean()