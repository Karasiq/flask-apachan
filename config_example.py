# coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))
MAX_CONTENT_LENGTH = 5 * 1024 * 1024; # 5 Мегабайт
IMG_FOLDER = 'files'

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/borda?charset=utf8'

CAPTCHA_ENABLED = True
RECAPTCHA_ENABLED = False
RECAPTCHA_PUBLIC_KEY = 'INSERT YOUR PUBLIC KEY'
RECAPTCHA_PRIVATE_KEY = 'INSERT YOUR PRIVATE KEY'

COOKIES_MAX_AGE = 2592000
CSRF_ENABLED = True
SECRET_KEY = 'changemechangemechangemechangeme'
ADMIN_PASS_MD5 = '4cb9c8a8048fd02294477fcb1a41191a' #'changeme'
BASE_RANDOMPIC_DIR = 'rsfiles'
DEBUG_ENABLED = False
RANDOM_SETS = [
	{
		'name' : u'Random'
    },
    {
        'dir' : 'random1',
        'name' : u'Рандом1'
    },
	{
		'dir' : 'random2',
		'name' : u'Рандом2'
	}
]

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yoursite.com']
TRASH = 'trash'
SECTIONS = { 'b' : u'Бред',
             't' : u'Тест',
			 'trash' : u'Помойка'}