from database import db


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = db.Column(db.Integer, primary_key = True)
    rating = db.Column(db.Integer, default=0)
    first_post = db.Column(db.DateTime)
    last_post = db.Column(db.DateTime)
    last_ip = db.Column(db.String(15))
    last_useragent = db.Column(db.String(200))
    banned = db.Column(db.Boolean, default = False)
    banexpiration = db.Column(db.DateTime)
    banreason = db.Column(db.String(100))
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    fingerprint = db.Column(db.String(100), default='')


class Post(db.Model):
    __tablename__ = 'post'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50))
    message = db.Column(db.String(5000))
    time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    from_ip = db.Column(db.String(15))
    image = db.Column(db.String(260), default='')
    thumb = db.Column(db.String(260), default='')
    rating = db.Column(db.Integer, default=0)
    randid = db.Column(db.Integer, default=0)
    # Only answer field:
    parent = db.Column(db.Integer, default=0)
    answer_to = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer, default=0)
    # Threads field
    answers = db.Column(db.Integer, default=0)
    last_answer = db.Column(db.DateTime)
    section = db.Column(db.String(5))

class Vote(db.Model): # Vote history
    __tablename__ = 'vote'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    value = db.Column(db.Integer, default = 0)