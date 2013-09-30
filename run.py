#!/usr/bin/python
# coding=utf-8

if __name__ == '__main__':
    import sys
    from app import app, load_config
    load_config()
    if '-debug' in sys.argv:
        app.run(debug=True, port=app.config['DEBUG_PORT'], host=app.config['DEBUG_HOST'])
    else:
        app.run(debug=False, threaded=True, port=app.config['PORT'], host=app.config['HOST'])