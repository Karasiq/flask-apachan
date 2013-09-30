# coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))
MAX_CONTENT_LENGTH = 5 * 1024 * 1024; # 5 Мегабайт
IMG_FOLDER = 'files'

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@host/dbname?charset=utf8'

CAPTCHA_ENABLED = True
RECAPTCHA_ENABLED = False
RECAPTCHA_PUBLIC_KEY = 'changeme'
RECAPTCHA_PRIVATE_KEY = 'changeme'

COOKIES_MAX_AGE = 2592000
CSRF_ENABLED = True
SECRET_KEY = 'changemechangemechangemechangeme'
ADMIN_PASS_MD5 = '4cb9c8a8048fd02294477fcb1a41191a' #'changeme'
BASE_RANDOMPIC_DIR = 'randompic_files'
DEBUG_ENABLED = False
SITE_NAME = 'site name'
USER_UNICAL_IPS = True
MAX_POSTS_ON_PAGE = 30
RATING_BAN_VOTE = 20
RANDOM_SETS = [
	{
		'name' : u'Random'
    },
    {
        'dir' : '1',
        'name' : u'Рандом-1'
    },
	{
		'dir' : '2',
		'name' : u'Рандом-2'
	}
]

SERVER_NAME = 'localhost:5000' if DEBUG_ENABLED else 'host.com'
DEBUG_PORT = 5000
PORT = 80
DEBUG_HOST = '127.0.0.1'
HOST = '0.0.0.0'
IP_BLOCKLIST_FILE = 'blocklist.txt'
TRASH = 'trash'
SECTIONS = { 'b' : u'Бред',
             'a' : u'Анус',
			 'trash' : u'Помойка'}
			 
CAPTCHA_FILES = [ # in /captcha
    {
        'name' : u'Капча №1',
        'file' : 'captcha1.jpg'
    },
    {
        'name' : u'Капча №2',
        'file' : 'captcha2.jpg'
    }
]