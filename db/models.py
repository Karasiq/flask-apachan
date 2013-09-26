from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from database import Base

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(Integer, primary_key = True)
    rating = Column(Integer, default=0)
    first_post = Column(DateTime)
    last_post = Column(DateTime)
    last_ip = Column(String(15))
    last_useragent = Column(String(200))
    banned = Column(Boolean, default = False)
    banexpiration = Column(DateTime)
    banreason = Column(String(100))
    posts = relationship('Post', backref = 'author', lazy = 'dynamic')
    fingerprint = Column(String(100), default='')

    def __repr__(self):
        return '<User %r>' % (self.body)


class Post(Base):
    __tablename__ = 'post'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(Integer, primary_key = True)
    title = Column(String(50))
    message = Column(String(1000))
    time = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    from_ip = Column(String(15))
    image = Column(String(260), default='')
    thumb = Column(String(260), default='')
    rating = Column(Integer, default=0)
    randid = Column(Integer, default=0)
    # Only answer field:
    parent = Column(Integer, default=0)
    answer_to = Column(Integer, default=0)
    position = Column(Integer, default=0)
    # Threads field
    answers = Column(Integer, default=0)
    last_answer = Column(DateTime)
    section = Column(String(5))
    mysql_charset = 'utf8'
    mysql_engine='InnoDB'

    def __repr__(self):
        return '<Post %r>' % (self.body)

class Vote(Base): # Vote history
    __tablename__ = 'vote'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    post_id = Column(Integer, ForeignKey('post.id'))
    value = Column(Integer, default = 0)
    mysql_charset = 'utf8'
    mysql_engine='InnoDB'

    def __repr__(self):
        return '{Vote %d [%d] ==> %d}' % (self.user_id, self.value, self.post_id)