﻿# coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))
MAX_CONTENT_LENGTH = 5 * 1024 * 1024 # 5 Мегабайт
IMG_FOLDER = 'files'

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@host/dbname?charset=utf8'
import tempfile
#CACHE_CONFIG = {'CACHE_TYPE':'redis', 'CACHE_KEY_PREFIX':'flask-apachan', 'CACHE_REDIS_URL':'redis://redis-addr.com:6379/0'}
CACHE_CONFIG = {'CACHE_TYPE':'filesystem', 'CACHE_DIR' : os.path.join(tempfile.gettempdir(), 'flask-apachan-cache')}
CACHING_TIMEOUT = 600 # 10 min

LOG_FILE = 'flask-apachan.log'

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
SYSTEM_WIDE_FP = False
MAX_POSTS_ON_PAGE = 30

DISABLE_RATING = False
RATING_CANVOTE = 0 # Disabled
RATING_TRASH = -5
RATING_BAN = -30

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

DEBUG_PORT = 5000
RELEASE_PORT = 80
DEBUG_HOST = 'localhost'
RELEASE_HOST = '0.0.0.0'
DEBUG_SERVER_NAME = None
RELEASE_SERVER_NAME = 'somehost.com'

from Crypto import Random
CRYPTO_IV = Random.new().read(16)

IP_BLOCKLIST_FILE = 'blocklist.txt'
TRASH = 'trash'
SECTIONS = { 'b' : u'Бред',
             'a' : u'Анус',
			 'trash' : u'Помойка',
             'hid' : u'Скрытый'}
DEFAULT_SECTION = 'b'
HIDDEN_BOARDS = ['hid']
			 
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