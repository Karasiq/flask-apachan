#!/usr/bin/python
# encoding=utf-8
import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'db'))
from app import db_session
from models import User, Post

def clean():
    users = User.query.filter_by(last_post = None)
    for u in users:
        print('User %d deleted' % u.id)
        db_session.delete(u)
    posts = Post.query.filter_by(parent = 0, answers = 0)
    for p in posts:
        print('Post %d deleted' % p.id)
        db_session.delete(p)
    db_session.commit()

if __name__ == '__main__':
    clean()