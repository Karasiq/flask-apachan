# coding=utf-8
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

WELCOME_TEXT = u'''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam mi risus, laoreet sed sapien ac, mollis cursus arcu. Duis id ultricies magna. In convallis nisl nec diam consequat volutpat. Quisque dapibus vel nibh sit amet facilisis. Cras dui sem, convallis at eleifend at, rhoncus vitae nisl. Etiam in felis id ante porttitor porttitor in in turpis. Praesent tristique at quam sit amet laoreet. In hac habitasse platea dictumst. Sed eu auctor elit, at lacinia orci. Quisque sed enim id enim ullamcorper fringilla eu et purus. Suspendisse aliquam elit elit, eu vehicula nulla volutpat in. Sed ut diam neque. Curabitur porta congue tortor, id dapibus leo commodo eu. Aenean commodo dictum sem, nec volutpat magna molestie in. Nulla facilisi. Mauris sed cursus odio.

Proin cursus mattis lacus, at semper nibh aliquet sit amet. Proin ac diam sollicitudin, aliquam eros a, semper justo. Morbi a turpis ultrices, congue nibh vitae, ultrices turpis. Pellentesque posuere sapien sed quam faucibus dignissim. Etiam semper eu purus sit amet egestas. Fusce nibh sapien, mattis vel justo ultricies, ullamcorper porta massa. Aenean iaculis libero et porttitor cursus. Fusce enim dolor, condimentum a mi vel, tempor euismod enim. Vivamus pulvinar tortor eget convallis ullamcorper. Pellentesque hendrerit augue a ante posuere tincidunt. In venenatis lobortis urna sit amet porttitor. Proin aliquam accumsan sodales.

Aliquam eget accumsan ligula, ac iaculis erat. Phasellus sit amet sodales nibh. Praesent viverra, purus sed lobortis condimentum, odio nulla consequat nulla, quis bibendum nisl orci vel justo. Suspendisse potenti. Nullam elementum eleifend sem a vehicula. Nulla lobortis, lectus sed luctus elementum, leo sapien malesuada est, sit amet malesuada libero purus et nisl. Nunc in orci pretium nisl adipiscing venenatis. Vivamus placerat feugiat enim, eu pharetra nunc accumsan et. Ut eleifend arcu sed sapien consequat iaculis. Sed et nisl consectetur, elementum nulla vitae, iaculis dolor. Suspendisse venenatis leo libero, et convallis dolor lobortis a. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus justo nibh, eleifend sed velit a, convallis gravida felis.

Sed risus justo, mollis et facilisis at, rhoncus non nisi. Vestibulum ultrices mattis metus ut lacinia. Mauris massa diam, posuere vitae mollis vitae, sodales vel diam. Ut et laoreet nunc. Quisque eu elit aliquam, iaculis ligula ut, varius ipsum. Donec at egestas tortor. Aliquam pretium urna lorem, et placerat velit semper eget. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Quisque dictum lorem id sem congue, at rhoncus elit lacinia. Mauris a venenatis nunc. Phasellus non magna interdum, egestas arcu nec, aliquam purus. Fusce vehicula dui mi, vitae tincidunt nisi gravida ac. Donec sodales purus nec suscipit consequat.

Nullam gravida, nunc ac dictum malesuada, libero nisl ornare tortor, ac egestas leo velit a sapien. Vivamus id velit iaculis, aliquet nibh at, tincidunt nisl. Curabitur massa mi, aliquam nec eleifend vitae, imperdiet ultrices lectus. Donec vitae eros sit amet arcu convallis ultricies ac sit amet lectus. Proin bibendum pellentesque nisi quis gravida. Quisque bibendum non tellus a aliquam. Vivamus in imperdiet justo. In rutrum ipsum scelerisque turpis venenatis aliquam. Nam vestibulum nunc vel est consequat cursus ut ac sem. Sed suscipit, orci vel varius cursus, enim libero sodales odio, ut imperdiet neque arcu non nisi. Pellentesque suscipit vulputate rutrum. Vivamus nec diam in nibh interdum tincidunt vitae non dolor. Aliquam erat volutpat. Nulla vel nulla convallis, egestas nisl quis, rhoncus libero. Duis non mauris sed est mollis posuere. Nam imperdiet, tellus non volutpat iaculis, orci enim tristique nisi, quis ornare nibh diam ac mauris.'''

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