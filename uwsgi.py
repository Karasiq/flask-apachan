#!/usr/bin/python
# coding=utf-8
from app import app
if app.config.get('DEBUG_ENABLED'):
	app.debug=True
	from werkzeug.debug import DebuggedApplication
	app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
