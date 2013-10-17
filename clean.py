#!/usr/bin/python
# encoding=utf-8
import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'db'))
from app import db_session
from models import User, Post

def clean():
    from app import del_post
    users = User.query.filter_by(last_post = None)
    for u in users:
        db_session.delete(u)
        print('User %d deleted' % u.id)
    posts = Post.query.filter_by(parent = 0, answers = 0)
    for p in posts:
        del_post(p, False)
        print('Post %d deleted' % p.id)
    db_session.commit()
    from cached import flush_cache
    flush_cache()

if __name__ == '__main__':
    clean()