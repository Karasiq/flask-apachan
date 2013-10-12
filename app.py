# coding=utf-8
from flask import Flask, render_template, request, redirect, make_response, session, send_from_directory, jsonify, url_for, flash
from flask.ext.assets import Environment, Bundle
from flask.ext.cache import Cache
from werkzeug import secure_filename
from flask.ext.sqlalchemy import SQLAlchemy
from forms import PostForm
from datetime import datetime, timedelta
import ipcheck, captcha
import os, sys, tempfile

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE':'filesystem', 'CACHE_DIR' : os.path.join(tempfile.gettempdir(), 'flask-apachan-cache')})
assets = Environment(app)
import models
from database import db_session

def dispatch_token(encrypted):
    from Crypto.Cipher import AES
    import base64

    IV = app.config['CRYPTO_IV']
    aes = AES.new(app.config['SECRET_KEY'], AES.MODE_CFB, IV)
    return aes.decrypt(base64.b64decode(encrypted))

def auth_token(id):
    from Crypto.Cipher import AES
    import base64

    IV = app.config['CRYPTO_IV']
    aes = AES.new(app.config['SECRET_KEY'], AES.MODE_CFB, IV)
    return base64.b64encode(aes.encrypt(str(id)))

def refresh_user(user):
    if session.get('fingerprint'):
        user.fingerprint = session.get('fingerprint')
    user.last_ip = request.remote_addr
    user.last_useragent = request.headers.get('User-Agent')
    db_session.add(user)
    db_session.commit()

@app.route('/redirect')
def external_redirect():
    import base64
    from jinja2 import Markup
    try:
        url = Markup.escape(base64.b64decode(request.args.get('url')))
        if url[:4] != 'http':
            return render_template("error.html", errortitle=u'Не надо так делать')
        return redirect(url)
    except:
        return redirect(redirect_url())

@app.route('/set_id')
def set_uid(uid = 0):
    if session.get('uid') == uid:
        return '1'

    if uid == 0 and (session.get('uid') or not session.get('fingerprint')):
        return '0'

    if uid == 0:
        try:
            session['uid'] = dispatch_token(request.args.get('uid', 0, type=int))
        except:
            session['uid'] = None
            return register()
    else:
        session['uid'] = uid # from register()

    user = db_session.query(models.User).filter_by(id = session['uid']).first()
    if user:
        session['banned'] = user.banned and datetime.now() < user.banexpiration

        ipbans = db_session.query(models.User).filter_by(last_ip = request.remote_addr, banned = True)
        for ipban in ipbans:
            if datetime.now() < ipban.banexpiration:
                user.banned = True
                user.banexpiration = ipban.banexpiration
                user.banreason = u'Забанен по айпи'
                db_session.add(user)
                db_session.commit()
                session['banned'] = True
                break

        if user.banned and datetime.now() >= user.banexpiration: # Снятие бана
            user.banned = False
            user.banexpiration = None
            user.banreason = None
            user.rating = 0 # Сброс
            db_session.add(user)
            db_session.commit()
        elif user.rating < (app.config['RATING_BAN_VOTE'] * -1):
            user.banned = True
            user.banexpiration = datetime.now() + timedelta(days = 10)
            user.banreason = u'Бан по сумме голосов (вероятно за идиотизм)'
            db_session.add(user)
            db_session.commit()

        if user.first_post and user.last_post and user.rating:
            session['canvote'] = session.get('admin') or ((datetime.now() - user.first_post) >= timedelta(days=14)
                                 and (datetime.now() - user.last_post) <= timedelta(days=3)
                                 and user.rating >= app.config['RATING_BAN_VOTE'] and not session['banned'])

        if request.cookies.get('admin'):
            import hashlib
            try:
                session['admin'] = (hashlib.md5(dispatch_token(request.cookies.get('admin'))) == app.config['ADMIN_PASS_MD5'])
            except:
                session['admin'] = False
    else: # Новый юзер
        return redirect(url_for('register'))
        #session['canvote'] = False
        #session['banned'] = False
    refresh_user(user)
    response = make_response(u'1')
    response.set_cookie('uid', auth_token(session.get('uid')), max_age=app.config['COOKIES_MAX_AGE'])
    session.permanent = True
    return response

@cache.memoize()
def get_safe_url(url):
    import base64
    if not app.config.get('SERVER_NAME') or get_netloc(url) != app.config['SERVER_NAME']:
        return url_for('external_redirect', url=base64.b64encode(url))
    else:
        return url

@cache.memoize(timeout=500)
@app.template_filter('ext_urls')
def escape_ext_urls(txt):
    import re
    result = txt
    matches = re.finditer(r'\bhref="(https?://[^"\r\n]*)"', txt)
    for m in matches:
        result = result.replace(m.group(0), 'href=\"%s\"' % get_safe_url(m.group(1)))
    return result

@cache.memoize(timeout=500)
@app.template_filter('message')
def render_message(msg):
    #from jinja2 import Markup
    import re
    r = msg
    r = re.sub(r'\[quote](.*)\[/quote\]', '<div class="quote">\\1</div>', r)
    r = re.sub(r'\[spoiler](.*)\[/spoiler\]', "<a style=\"background:darkgray;color:darkgray\" onmouseover=\"this.style.color=\'white';\" onmouseout=\"this.style.color=\'darkgray\';\">\\1</a>", r)
    r = re.sub(r'\[b](.*)\[/b\]', '<b>\\1</b>', r)
    r = re.sub(r'\[u](.*)\[/u\]', '<u>\\1</u>', r)
    r = re.sub(r'\[s](.*)\[/s\]', '<s>\\1</s>', r)
    r = re.sub(r'\[i](.*)\[/i\]', '<i>\\1</i>', r)
    r = re.sub(r'\[url](?!javascript:)([^\r\n]*)\[/url\]', '<a href=\"\\1\">\\1</a>', r)
    r = re.sub(r'\[url="?(?!javascript:)([^\r\n]*)"?\](?!javascript:)(.*)\[/url]', '<a href=\"\\1\">\\2</a>', r)
    r = re.sub(r'https?://(?:www\.)youtube\.com/watch\?[\w\-&%=]*\bv=([\w-]*)', render_template("youtube.html"), r)
    if app.config.get('SERVER_NAME'):
        r = re.sub(r'(?<!")(?<!">)\bhttps?://' + app.config['SERVER_NAME'] + r'/([^"\s<>]*)', '<a href=\"/\\1\">/\\1</a>', r) # relative
    r = re.sub(r'(?<!")(?<!">)\b(https?://[^"\s<>]*)', '<a href=\"\\1\">\\1</a>', r)
    return r.replace('\r\n', '<br>')

@app.route('/_vote')
def vote():
    val = request.args.get('vote', 0, type=int)
    pid = request.args.get('postid', 0, type=int)
    if not val or not pid:
        return render_template("error.html", errortitle=u"Ошибка голосования")
    post = db_session.query(models.Post).filter_by(id = pid).first()
    if session.get('canvote'):
        user = db_session.query(models.User).filter_by(id = session['uid']).first()
        vote = db_session.query(models.Vote).filter_by(user_id = user.id, post_id = post.id).first()
        if user and post and user.id != post.user_id and not vote and not (val > 1 or val < -1):
            vote = models.Vote(post_id = post.id, user_id = user.id, value = val)
            post.rating += val
            if post.rating <= -5:
                post.section = app.config['TRASH'] # Перенос в помойку
                answers = db_session.query(models.Post).filter_by(parent = post.id)
                for a in answers:
                    a.section = app.config['TRASH']
                    db_session.add(a)
            author = db_session.query(models.User).filter_by(id = post.user_id).first()
            if author:
                author.rating += val
                db_session.add(author)
            db_session.add(post)
            db_session.add(vote)
            db_session.commit()

    return str(post.rating)

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


@app.route('/set-fp', methods=['GET', 'POST'])
def set_fp():
    if not session.get('fingerprint'):
        session['fingerprint'] = request.args.get('fp')
        u = db_session.query(models.User).filter_by(fingerprint = session['fingerprint']).first()
        if not u:
            if session.get('uid'):
                u = db_session.query(models.User).filter_by(id = session.get('uid')).first()
            if not u:
                return redirect(url_for('register'))
        set_uid(u.id)
        u.last_useragent = request.headers.get('User-Agent')
        u.last_ip = request.remote_addr
        u.fingerprint = session['fingerprint']
        db_session.add(u)
        db_session.commit()
    return '1'

@app.route('/reg')
def register():
    from sqlalchemy import or_
    if not session.get('fingerprint'):
        return redirect(redirect_url())

    if not session.get('uid'):
        rec = db_session.query(models.User).filter(or_(models.User.fingerprint == session.get('fingerprint'), models.User.last_ip == request.remote_addr)).first() if app.config['USER_UNICAL_IPS'] else db_session.query(models.User).filter(models.User.fingerprint == session.get('fingerprint')).first()
        if rec is None:
            rec = models.User(last_ip = request.remote_addr, last_useragent = request.headers.get('User-Agent'), fingerprint = session.get('fingerprint'))
            db_session.add(rec)
            db_session.commit()
        #session['uid'] = rec.id
        if rec and rec.id:
            set_uid(rec.id)
        response = make_response(redirect(redirect_url()))
        #response = make_response(render_template("index.html", setid = auth_token(rec.id)))
        response.set_cookie('uid', auth_token(rec.id) if rec and rec.id else '', max_age=app.config['COOKIES_MAX_AGE'])
        return response
    return redirect(redirect_url())

@app.before_request
def user_check():
    if not request.endpoint or request.endpoint.split('.')[0] not in ['captcha', 'register', 'static', 'set_uid', 'set_fp']:
        if app.config['RECAPTCHA_ENABLED'] and (not session.get('human-test-validity') or session.get('human-test-validity') < datetime.now()):
            return redirect(url_for('human_test'))
        elif app.config['CAPTCHA_ENABLED'] and (not session.get('captcha-resolve')):
            return redirect(url_for('captcha.show_captcha'))
    #if request.headers.get('Host') != app.config['SERVER_NAME']:
    #    return redirect('http://google.com/')
    if not session.get('uid') and session.get('fingerprint') and (not request.endpoint or request.endpoint not in ['register', 'static', 'set_uid', 'set_fp']):
        return redirect(url_for('register'))
    if app.config['IP_BLOCKLIST'].InList(request.remote_addr):
        return render_template('error.html', errortitle=u'Этот IP-адрес заблокирован')

    #return True, ''

@cache.cached()
@app.route('/index')
@app.route('/')
def index():
    #result, response = user_check()
    #if not result: return response
    return render_template("index.html", sections = app.config['SECTIONS'])

def get_page_number(post):
    return post.position / app.config['MAX_POSTS_ON_PAGE'] if post.position else 0

@cache.memoize()
@app.route('/viewpost/<postid>') # Посмотреть пост в треде
def viewpost(postid):
    #result, response = user_check()
    #if not result: return response
    post = db_session.query(models.Post).filter_by(id = postid).first()
    if post:
        if post.parent == 0:
            return redirect(url_for('view', postid = postid))
        else:
            return redirect(url_for('view', postid=post.parent, page=get_page_number(post)) + '#t' + str(postid))
@cache.memoize()
def id_list(posts):
    il = list()
    for p in posts:
        il.append(p.id)
    return il

#@cache.memoize(timeout=20)
@app.route('/semenodetector/<postid>')
@app.route('/semenodetector/<postid>/<page>')
def semeno_detector(postid, page=0):
    #result, response = user_check()
    #if not result: return response
    post = db_session.query(models.Post).filter_by(id = postid).first()
    if post:
        parent_id = post.parent if post.parent != 0 else post.id
        posts = db_session.query(models.Post).filter(models.Post.user_id == post.user_id, models.Post.parent == parent_id, models.Post.id != postid).order_by(models.Post.id.asc())
        est = posts.count() - app.config['MAX_POSTS_ON_PAGE']
        posts = posts.limit(app.config['MAX_POSTS_ON_PAGE'])
        form = PostForm()
        form.answer_to.data = postid
        if int(post.parent) == 0:
            form.parent.data = post.id
        else:
            form.parent.data = post.parent
        form.section.data = post.section
        return render_template("section.html", SecName = u'Семенодетектор (#%s)' % int(postid), posts = posts, form = form, mainpost = post, 
                               randoms = app.config['RANDOM_SETS'], est = est, page = int(page), baseurl = '/semenodetector/' + postid + '/', 
                               page_posts = id_list(posts))

@app.route('/add-to-favorites')
def add_to_favorites():
    thid = int(request.args.get('thid'))
    if not session.get('favorites'):
        session['favorites'] = list()
    if thid not in session['favorites']:
        session['favorites'].append(thid)
        return jsonify(result=url_for('static', filename='unfav.png'))
    else:
        session['favorites'].remove(thid)
        return jsonify(result=url_for('static', filename='fav.png'))

@app.route('/unhide-threads')
def unhide_threads():
    session['hidden'] = []
    return redirect(redirect_url())

@app.route('/hide-thread')
def hide_thread():
    thid = int(request.args.get('thid'))
    if not session.get('hidden'):
        session['hidden'] = list()
    session['hidden'].append(thid)
    return jsonify(result=True)

#@cache.memoize(timeout=10)
@app.route('/mythreads')
def mythreads():
    #result, response = user_check()
    #if not result: return response
    posts = db_session.query(models.Post).filter(models.Post.user_id == session.get('uid'), models.Post.parent == 0).order_by(models.Post.last_answer.desc())
    return render_template("section.html", SecName = u'Мои треды', posts = posts, 
                           randoms = app.config['RANDOM_SETS'], baseurl = '/mythreads/', 
                           page_posts = id_list(posts))
#@cache.memoize(timeout=10)
@app.route('/answers')
def answers():
    #result, response = user_check()
    #if not result: return response

    posts = db_session.query(models.Post).filter_by(user_id = session.get('uid')).order_by(models.Post.time.desc())
    ids = list()
    for p in posts:
        ids.append(p.id)
    answers = db_session.query(models.Post).filter(models.Post.answer_to.in_(ids)).order_by(models.Post.time.desc())
    return render_template("section.html", SecName = u'Ответы', posts = answers, 
                           randoms = app.config['RANDOM_SETS'], baseurl = '/answers/', 
                           page_posts = id_list(answers), show_answer_to = True)

@app.route('/favorites')
def favorites():
    #result, response = user_check()
    #if not result: return response

    if session.get('favorites'):
        posts = db_session.query(models.Post).filter(models.Post.id.in_(session['favorites'])).order_by(models.Post.id.asc())
        return render_template("section.html", SecName = u'Избранное', posts = posts, 
                               randoms = app.config['RANDOM_SETS'], baseurl = '/favorites/', 
                               page_posts = id_list(posts))
    else:
        return render_template('error.html', errortitle=u'В избранном ничего нет')

#@cache.memoize(timeout=20)
@app.route('/view/<postid>')
@app.route('/view/<postid>/<page>')
def view(postid, page=0):
    from sqlalchemy import or_
    #result, response = user_check()
    #if not result: return response
    post = db_session.query(models.Post).filter_by(id = postid).first()
    answers = db_session.query(models.Post).filter(or_(models.Post.parent == postid, models.Post.answer_to == postid)).order_by(models.Post.id.asc()).offset(int(page) * app.config['MAX_POSTS_ON_PAGE'])
    est = answers.count() - app.config['MAX_POSTS_ON_PAGE']
    answers = answers.limit(app.config['MAX_POSTS_ON_PAGE'])

    if post is None:
        return render_template("error.html", errortitle = u"Пост не найден")
    form = PostForm()
    form.answer_to.data = post.id
    if int(post.parent) == 0:
        form.parent.data = post.id
    else:
        form.parent.data = post.parent
    form.section.data = post.section

    return render_template("section.html", SecName = app.config['SECTIONS'][post.section], posts = answers, form = form, mainpost = post, 
                           randoms = app.config['RANDOM_SETS'], est = est, page = int(page), baseurl = '/view/' + postid + '/', 
                           page_posts = id_list(answers))

def unique_id():
    import hashlib, uuid
    return hashlib.md5(hex(uuid.uuid4().time)[2:-1]).hexdigest()

@app.route('/human-test', methods=['GET', 'POST'])
def human_test():
    from forms import HumanTestForm
    form = HumanTestForm()
    if form.validate_on_submit():
        session['human-test-validity'] = datetime.now() + timedelta(days = 3)
        return redirect(url_for('index'))
    else:
        return render_template('recaptcha.html', form = HumanTestForm())

@cache.memoize()
def get_netloc(url):
    import urlparse
    return urlparse.urlparse(url).netloc

@cache.memoize()
@app.route('/img/<randid>/<filename>', methods=['GET'])
def getimage(randid, filename):
    #if not request.headers.get('Referer') or get_netloc(request.headers.get('Referer')).split(':')[0] not in app.config['ALLOWED_HOSTS']:
    #    return send_from_directory('static', 'hotlink.png')
    if int(randid) == 0:
        return send_from_directory(app.config['IMG_FOLDER'], filename)
    else:
        return send_from_directory(os.path.join(app.config['BASE_RANDOMPIC_DIR'], app.config['RANDOM_SETS'][int(randid)]['dir']), filename)

def del_post(post, commit = True): # Рекурсивное удаление поста
    from sqlalchemy import or_
    if post.parent != 0:
        parent = db_session.query(models.Post).filter_by(id = post.parent).first()
        if parent.last_answer == post.time:
            last_post = db_session.query(models.Post).filter(models.Post.parent == parent.id, models.Post.id != post.id).order_by(
                        models.Post.time.desc()).first()
            if last_post:
                parent.last_answer = last_post.time
        parent.answers -= 1
        db_session.add(parent)
    childs = db_session.query(models.Post).filter(or_(models.Post.answer_to == post.id, models.Post.parent == post.id))
    for c in childs:
        del_post(c, False)
    db_session.delete(post)
    if commit:
        db_session.commit()

@app.route('/delpost')
def postdel():
    postid = int(request.args.get('postid'))
    post = db_session.query(models.Post).filter_by(id = postid).first()
    if not session.get('admin') and (not postid in session.get('can_delete') or not post or post.user_id != int(session.get('uid'))):
        return render_template("error.html", errortitle=u'Ошибка удаления поста')

    del_post(post, True)
    if post.parent == 0:
        return redirect(url_for('section', SectionName=post.section))
    else:
        return redirect(url_for('viewpost', postid=post.parent))

def thread_transfer(thid, new_section):
    from sqlalchemy import or_
    post = db_session.query(models.Post).filter_by(id = thid).first()

    if post and post.parent == 0:
        post.section = new_section
        db_session.add(post)
        childs = db_session.query(models.Post).filter_by(parent = thid)
        for c in childs:
            c.section = new_section
            db_session.add(c)
        db_session.commit()

@app.route('/admin/totrash')
def admin_totrash():
    if not session.get('admin'):
        return redirect(url_for('index'))
    thid = int(request.args.get('thread_id'))
    thread_transfer(thid, app.config['TRASH'])
    return '1'

@app.route('/admin/del_ip')
def admin_delip():
    if not session.get('admin'):
        return redirect(url_for('index'))
    ip = request.args.get('ipaddr')
    posts = db_session.query(models.Post).filter_by(from_ip = ip)
    for p in posts:
        del_post(p, False)
    users = db_session.query(models.User).filter_by(last_ip = ip)
    for u in users:
        u.banned = True
        u.banexpiration = datetime.now() + timedelta(days = 30)
        u.banreason = u'Забанен модератором по айпи'
        db_session.add(u)

    db_session.commit()
    return '1'

@app.route('/admin/ban')
def admin_ban(userid = 0):
    if userid == 0:
        userid = int(request.args.get('userid'))
    if not session.get('admin'):
        return redirect(url_for('index'))
    user = db_session.query(models.User).filter_by(id = userid).first()
    if user:
        user.banned = True
        user.banexpiration = datetime.now() + timedelta(days = 30)
        user.banreason = u'Забанен модератором'
        db_session.add(user)
        db_session.commit()
    return '1'

@app.route('/admin/delall')
def admin_delall():
    if not session.get('admin'):
        return redirect(url_for('index'))
    userid = request.args.get('userid')
    posts = db_session.query(models.Post).filter_by(user_id = userid)
    for p in posts:
        del_post(p, False)
    db_session.commit()
    print(u'Все посты пользователя %d удалены' % int(userid))
    return admin_ban(userid)

@app.route('/admin/login')
def admin_login():
    import hashlib
    if (hashlib.md5(request.args.get('p')).hexdigest() == app.config.get('ADMIN_PASS_MD5')) or request.remote_addr == '127.0.0.1':
        session['admin'] = True
    r = make_response(redirect(redirect_url()))
    #r.set_cookie('admin', auth_token(request.args.get('p')), max_age=app.config['COOKIES_MAX_AGE'])
    return r

RANDOM_IMAGES = list() # init at run
def get_randompic(num):
    from random import choice
    randoms = app.config['RANDOM_SETS']
    if num == 0 or num > len(randoms):
        return 0, '' # Ошибка
    return num, choice(RANDOM_IMAGES[num - 1])

@app.route('/report')
def report():
    #postid = request.args.get('post_id')
    return render_template("error.html", errortitle = u'Анус себе заарбузь')

@app.route('/post', methods=['POST'])
def post():
    import imghdr, hashlib, tempfile, pycurl, StringIO
    from PIL import Image
    import images2gif

    #result, response = user_check()
    #if not result: return response

    if session.get('banned'):
        user = db_session.query(models.User).filter_by(id = session.get('uid')).first()
        if user and user.banreason:
            return render_template("error.html", errortitle = u"Вы забанены и не можете постить тут.\r\nПричина: %s" \
                                % user.banreason)
        else:
            return render_template("error.html", errortitle = u"Вы забанены и не можете постить тут.")

    form = PostForm()
    if form.validate_on_submit():
        form.msg.data = form.msg.data.strip()
        form.title.data = form.title.data.strip()
        if not len(form.msg.data) and int(form.parent.data) == 0:
            return render_template("error.html", errortitle = u"Нельзя запостить пустой тред")
        if app.config['SECTIONS'].get(form.section.data) is None:
            return render_template("error.html", errortitle = u"Раздел не найден")

        user = db_session.query(models.User).filter_by(id = session['uid']).first()
        if user is None:
            return redirect('/reg')
        if user.banned and (datetime.now() < user.banexpiration):
            return render_template("error.html", errortitle = u"Вы забанены и не можете постить тут: " + user.banreason)

        if not session.get('admin') and user.last_post is not None and (datetime.now() - user.last_post) < timedelta(seconds = 30):
            return render_template("error.html", errortitle = u"Пост можно отправлять не чаще, чем раз в 30 секунд")

        if not session.get('admin') and user.last_post is not None and (datetime.now() - user.last_post) < timedelta(minutes = 3) and form.parent == 0:
            return render_template("error.html", errortitle = u"Треды можно создавать не чаще, чем раз в 3 минуты")

        from jinja2 import Markup
        entry = models.Post(title = form.title.data, message = unicode(Markup.escape(form.msg.data)), time = datetime.now(), parent = int(form.parent.data),
                            answer_to = int(form.answer_to.data), section = form.section.data,
                            from_ip = request.remote_addr, user_id = user.id, thumb = '', image = '', last_answer = datetime.now())

        if entry.parent != 0:
            parent = db_session.query(models.Post).filter_by(id = entry.parent).first()
            if entry.answer_to != entry.parent:
                answer = db_session.query(models.Post).filter_by(id = entry.answer_to).first()
                if not answer or answer.parent != entry.parent:
                    return render_template("error.html", errortitle = u"Неверные данные")
            if parent:
                entry.position = parent.answers
                parent.answers += 1
                if not form.sage.data:
                    parent.last_answer = entry.time
                db_session.add(parent)

        rand = int(form.ins_random.data)
        if rand != 0: # randompic
            entry.randid, entry.image = get_randompic(rand)
            entry.thumb = entry.image
        else:
            blob = None
            imgfile = None
            imgdir = app.config['IMG_FOLDER']
            if len(form.img_url.data) > 0: # from url
                from urlparse import urlparse
                c = pycurl.Curl()
                buf = StringIO.StringIO()
                try:
                    _url = urlparse(form.img_url.data)
                    c.setopt(pycurl.URL, (_url.scheme + '://' + _url.netloc.encode('idna') + _url.path).encode('utf-8'))
                    c.setopt(pycurl.WRITEFUNCTION, buf.write)
                    c.setopt(pycurl.FOLLOWLOCATION, 1)
                    c.perform()
                    imgfile = tempfile.TemporaryFile()
                    imgfile.write(buf.getvalue())
                    imgfile.seek(0, 0)
                except:
                    return render_template("error.html", errortitle=u'Ошибка загрузки изображения')

            elif 'img' in request.files: # from file
                imgfile = request.files.get('img')

            blob = imgfile.read()
            if len(blob) > 0:
                type = imghdr.what('', blob)
                if not type:
                #shutil.rmtree(imgdir)
                    return render_template("error.html", errortitle = u"Неверный файл изображения")

                imgfilename = hashlib.md5(blob).hexdigest() + '.' + type
                aimgfilename = os.path.join(imgdir, imgfilename)
                thumbfilename, thumbext = os.path.splitext(imgfilename)
                thumbfilename = thumbfilename + '_thumb' + thumbext

                if not os.path.exists(aimgfilename) or not os.path.exists(thumbfilename):
                    if not os.path.exists(imgdir):
                        os.makedirs(imgdir)
                    with open(aimgfilename, "wb") as imgf:
                        imgf.write(blob)
                        imgf.close()

                    thumbsize = 200, 200
                    img = None
                    if type == 'gif':
                        frames = images2gif.readGif(aimgfilename, False)
                        img = frames[0]
                    else:
                        img = Image.open(aimgfilename)
                    img.thumbnail(thumbsize)
                    img.save(os.path.join(imgdir, thumbfilename), "JPEG")
                entry.thumb = thumbfilename
                entry.image = imgfilename

        if (entry.thumb == '' or entry.image == '') and entry.parent == 0:
            return render_template("error.html", errortitle=u'Нельзя запостить тред без картинки')

        user.last_ip = request.remote_addr
        user.last_useragent = request.headers.get('User-Agent')
        user.last_post = entry.time
        db_session.add(user)
        db_session.add(entry)

        db_session.commit()
        session['can_delete'] = session.get('can_delete') or list()
        session['can_delete'].append(entry.id)
        if entry.parent == 0:
            return redirect(url_for('view', postid=entry.id))
        else:
            return redirect(url_for('viewpost', postid=entry.id))
            # return redirect(url_for('view', postid=entry.parent))
    else:
        for error in form.errors:
                flash(error)
        return render_template("error.html", errortitle=u'Ошибка отправки')

@cache.memoize(timeout=100)
@app.route('/gallery')
@app.route('/gallery/<Page>')
def gallery(Page=0):
    posts = db_session.query(models.Post).filter(models.Post.randid == 0, models.Post.image != '').order_by(models.Post.last_answer.desc()).offset(int(Page) * app.config['MAX_POSTS_ON_PAGE'])
    est = posts.count() - app.config['MAX_POSTS_ON_PAGE']
    posts = posts.limit(app.config['MAX_POSTS_ON_PAGE'])
    return render_template("gallery.html", posts = posts, page = Page, pages = int(est / app.config['MAX_POSTS_ON_PAGE']))

#@cache.memoize(timeout=10)
@app.route('/all')
@app.route('/all/<Page>')
def allsections(Page=0):
    #result, response = user_check()
    #if not result: return response
    posts = db_session.query(models.Post).filter_by(parent = 0).order_by(models.Post.last_answer.desc()).offset(int(Page) * app.config['MAX_POSTS_ON_PAGE'])
    est = posts.count() - app.config['MAX_POSTS_ON_PAGE']
    posts = posts.limit(app.config['MAX_POSTS_ON_PAGE'])
    form = PostForm()
    form.parent.data = '0'
    form.section.data = 'b'
    return render_template("section.html", SecName = u'Поток', posts = posts, form = form, 
                           randoms = app.config['RANDOM_SETS'], show_section = True, est = est, page = int(Page),
                           baseurl = '/all/', )


#@cache.memoize(timeout=10)
@app.route('/boards/<SectionName>')
@app.route('/boards/<SectionName>/<Page>')
def section(SectionName, Page=0):
    #result, response = user_check()
    #if not result: return response
    if app.config['SECTIONS'].get(SectionName) is None:
        return render_template("error.html", errortitle = u"Раздел не найден")
    posts = db_session.query(models.Post).filter_by(parent = 0, section = SectionName).order_by(models.Post.last_answer.desc()).offset(int(Page) * app.config['MAX_POSTS_ON_PAGE'])
    est = posts.count() - app.config['MAX_POSTS_ON_PAGE']
    posts = posts.limit(app.config['MAX_POSTS_ON_PAGE'])
    form = PostForm()
    form.section.data = SectionName
    return render_template("section.html", SecName = app.config['SECTIONS'][SectionName], posts = posts, form = form, 
                           randoms = app.config['RANDOM_SETS'], page = int(Page), est = est, baseurl = '/boards/' + SectionName + '/',
                           )
# on start
from os import listdir
from os.path import isfile, join

app.config.from_object('config')
app.register_blueprint(captcha.captcha)

app.config['IP_BLOCKLIST'] = ipcheck.IpList()
if os.path.exists(app.config['IP_BLOCKLIST_FILE']):
    app.config['IP_BLOCKLIST'].Load(app.config['IP_BLOCKLIST_FILE'])

js = Bundle('fingerprint.js', 'jquery-2.0.3.min.js', 'evercookie.js', 'jsfunctions.js', 'images.js', filters=None if app.config['DEBUG_ENABLED'] else 'jsmin', output='gen/packed.js')
assets.register('js_all', js)

for r in app.config['RANDOM_SETS']:
    if r.has_key('dir') and os.path.exists(os.path.join(app.config['BASE_RANDOMPIC_DIR'], r.get('dir'))):
        onlyfiles = [ f for f in listdir(os.path.join(app.config['BASE_RANDOMPIC_DIR'], r['dir'])) if isfile(join(os.path.join(app.config['BASE_RANDOMPIC_DIR'], r['dir']), f)) ]
        RANDOM_IMAGES.append(onlyfiles)
