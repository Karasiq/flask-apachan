#!/usr/bin/python
# coding=utf-8
from app import app
if app.config['DEBUG_ENABLED']:
    app.debug=True
    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
    app.config['SERVER_NAME'] = app.config['DEBUG_SERVER_NAME']
else:
    app.config['SERVER_NAME'] = app.config['RELEASE_SERVER_NAME']
