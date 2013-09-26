# coding=utf-8
from flask import Blueprint, render_template, abort, session, redirect, request, send_from_directory

captcha = Blueprint('captcha', __name__,
                        template_folder='templates')

captcha_files = [
    {
        'name' : u'Ракодил',
        'file' : 'image033.jpg'
    },
    {
        'name' : u'Газ-кун',
        'file' : 'gazovik.jpg'
    },
    {
        'name' : u'Апацхе',
        'file' : 'apazhe-be-be-be.jpg'
    },
    {
        'name' : u'Хохол',
        'file' : 'pig3.jpg'
    },
    {
        'name' : u'Распальцовка',
        'file' : '283px-Sign_apachan.jpg'
    },
    {
        'name' : u'ТНН',
        'file' : 'Tnn.jpg'
    },
    {
        'name' : u'1000 WMR',
        'file' : '800px-Kop_anus.jpg'
    },
    {
        'name' : u'От спички норм будет',
        'file' : '267px-Gasapachan.jpg'
    },
    {
        'name' : u'Принцип-компани',
        'file' : 'vqgfls5k2220.jpg'
    },
]

@captcha.route('/get-captcha')
def get_captcha_img():
    import datetime
    from flask import make_response
    if not session.get('valid'):
        abort(403)

    response = make_response(send_from_directory('captcha', session['valid']['file']))

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
        if captcha_res and session.get('valid'):
            session['captcha-resolve'] = (captcha_res == session.get('valid')['name'])
            session['valid'] = None
        return jsonify(success = session.get('captcha-resolve'))

    if session.get('captcha-resolve') == True:
        session['valid'] = None
        return redirect('/index')

    names = list()
    for c in captcha_files:
        names.append(c['name'])
    shuffle(names)
    session['valid'] = choice(captcha_files)
    return render_template('captcha.html', names = names)