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

# How to install
* Database:
    * Change sqlalchemy.url in alembic.ini
    * Run `alembic upgrade head`
* Settings:
    * Rename config_example.py to config.py
    * Change settings in config.py
* Run the app: `python run.py`

# Issues
* Access error when generating assets/saving pictures
    Fix: `chmod +w ./static ./static/gen ./static/.webassets-cache [IMG_FOLDER from config.py]`
