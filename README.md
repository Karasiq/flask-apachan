flask-apachan
=============
# Required packages
* flask-sqlalchemy
* flask-wtf
* flask-assets
* flask-cache
* images2gif
* numpy
* pillow
* pycurl
* pycrypto
* yuicompressor
* alembic

# Author
Created by Bidon Pomoev <yoba123@yandex.ru>

# How to install
* Database:
    * Change sqlalchemy.url in alembic.ini
    * Run `alembic upgrade head`
* Settings:
    * Rename config_example.py to config.py
    * Change settings in config.py
* Run the app: `python run.py`