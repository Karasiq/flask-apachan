# coding=utf-8
from flask import Blueprint, request, jsonify, session
from flask.ext.assets import Environment, Bundle
import os
from app import app, assets
fingerprint = Blueprint('fingerprint', __name__)

@fingerprint.route('/get-uid')
def get_uid():
    if session.get('uid'):
        from app import auth_token
        return auth_token(session['uid'])
    else:
        return ''
    #import hashlib, uuid
    #return hashlib.md5(hex(uuid.uuid4().time)[2:-1]).hexdigest()

@fingerprint.route('/set-fp', methods=['POST'])
def set_fingerprint():
    import hashlib
    from app import set_fp_callback
    fp_hashes = dict()

    fp_hashes['browser'] = hashlib.md5(request.json['mimetypes'].encode('utf-8') + (request.json['fontlist'] or request.json['fonts_all']).encode('utf-8') + request.json['navigator_hash'].encode('utf-8')).hexdigest()
    fp_hashes['system'] = hashlib.md5(str(request.json['timezone']) + request.json['os'] + request.json['screen']).hexdigest()
    #fp_hashes['navigator'] = request.json['navigator_hash']
    fp_hashes['browser_hdrs'] = hashlib.md5(request.headers['Accept'] + request.headers['Accept-Language'] + request.headers['Accept-Encoding']).hexdigest()
    fp_hashes['system_browser'] = hashlib.md5(fp_hashes['system'] + fp_hashes['browser_hdrs']).hexdigest()

    return set_fp_callback(request.json['user_name'], fp_hashes)

# On run
deps_js = Bundle('javascript/swfobject.min.js', 'javascript/jquery.json-2.3.min.js', 'javascript/jquery.flash.js', 'javascript/evercookie/evercookie.js', 'javascript/sha1.js') # + Jquery
fp_js = Bundle('javascript/plugindetect/plugindetect.js', 'javascript/fontdetect.js', 'javascript/fingerprint.js')
assets.register('js_fingerprint', Bundle(deps_js, fp_js, filters='yui_js', output='gen/fingerprint.js'))