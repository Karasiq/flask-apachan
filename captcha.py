# coding=utf-8
from flask import Blueprint, render_template, abort, session, redirect, request, send_from_directory

captcha = Blueprint('captcha', __name__)

from config import CAPTCHA_FILES

@captcha.route('/get-captcha')
def get_captcha_img():
    import datetime
    from flask import make_response
    if not session.get('valid_captcha'):
        abort(403)

    response = make_response(send_from_directory('captcha', session['valid_captcha']['file']))

    response.headers.add('Last-Modified', datetime.datetime.now())
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    response.headers.add('Pragma', 'no-cache')

    return response

@captcha.route('/captcha', methods = ['POST', 'GET'])
def show_captcha():
    from random import shuffle, choice
    from flask import jsonify
    if request.args.get('c'):
        captcha_res = request.args.get('c')
        if captcha_res and session.get('valid_captcha'):
            session['captcha-resolve'] = (captcha_res == session.get('valid_captcha')['name'])
            session['valid_captcha'] = None
        return jsonify(success = session.get('captcha-resolve'))

    if session.get('captcha-resolve') == True:
        session['valid_captcha'] = None
        return redirect('/index')

    names = list()
    for c in CAPTCHA_FILES:
        names.append(c['name'])
    shuffle(names)
    if not session.get('valid_captcha'):
        session['valid_captcha'] = choice(CAPTCHA_FILES)
    return render_template('captcha.html', names = names)