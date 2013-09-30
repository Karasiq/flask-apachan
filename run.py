#!/usr/bin/python
# coding=utf-8

if __name__ == '__main__':
    import sys
    from app import app, load_config
    load_config()
    if '-debug' in sys.argv:
        app.config['SERVER_NAME'] = app.config['DEBUG_SERVER_NAME']
        app.run(debug=True, port=app.config['DEBUG_PORT'], host=app.config['DEBUG_HOST'])
    else:
        app.config['SERVER_NAME'] = app.config['RELEASE_SERVER_NAME']
        app.run(debug=False, threaded=True, port=app.config['RELEASE_PORT'], host=app.config['RELEASE_HOST'])