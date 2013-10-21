# coding=utf-8
from flask import Flask, render_template, request, redirect, make_response, session, send_from_directory, jsonify, url_for, flash
from flask.ext.assets import Environment, Bundle
from flask.ext.cache import Cache
from werkzeug import secure_filename
from forms import PostForm
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config.from_object('config')
cache = Cache(app, config=app.config['CACHE_CONFIG'])
assets = Environment(app)
from database import db_session
from models import Vote, User, Post

import ipcheck, captcha, flask_fingerprint
app.register_blueprint(captcha.captcha)
app.register_blueprint(flask_fingerprint.fingerprint)


def get_current_fingerprint():
    return session['fingerprint']['system'] if app.config['SYSTEM_WIDE_FP'] else session['fingerprint'][
        'browser']


@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def id_list(posts):
    if not posts: return []
    il = list()
    for p in posts:
        il.append(p.id)
    return il

from cached import flush_cache, flush_cached_user, get_posts, get_user, render_section, render_stream, render_view, render_answers, render_favorites, render_mythreads, render_semenodetector, render_gallery, render_ajax

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def dispatch_token(encrypted):
    from Crypto.Cipher import AES
    import base64

    IV = app.config['CRYPTO_IV']
    aes = AES.new(app.config['SECRET_KEY'], AES.MODE_CFB, IV)
    return aes.decrypt(base64.b64decode(encrypted))

@cache.memoize(timeout=100)
def auth_token(id):
    from Crypto.Cipher import AES
    import base64

    IV = app.config['CRYPTO_IV']
    aes = AES.new(app.config['SECRET_KEY'], AES.MODE_CFB, IV)
    return base64.b64encode(aes.encrypt(str(id)))

@cache.memoize(timeout=timedelta(days=1).seconds)
def refresh_user(user):
    if session.get('fingerprint'):
        user.fingerprint = get_current_fingerprint()
    user.last_ip = request.headers.get('X-Forwarded-For') or request.remote_addr
    user.last_useragent = request.headers.get('User-Agent')
    db_session.add(user)
    db_session.commit()
    flush_cached_user(user.id)
    return True

@app.route('/ajax/reload')
def ajax_reload():
    return render_ajax(request.args)

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

def ban_user(uid, banexpiration, banreason):
    user = get_user(uid)
    user.banned = True
    user.banexpiration = banexpiration
    user.banreason = banreason
    db_session.add(user)
    db_session.commit()
    flush_cached_user(user.id)
    if session and request and session.get('uid') == uid:
        session['banned'] = True

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def check_banned(session=session):
    user = get_user(session['uid'])
    return session.get('crawler') or session.get('banned') or (user and user.banned and datetime.now() < user.banexpiration)

def set_uid(uid):
    if session.get('uid') == uid:
        return jsonify(result=True)
    session['uid'] = uid
    user = get_user(uid)
    if user:
        session['banned'] = user.banned and datetime.now() < user.banexpiration

        if app.config['USER_UNICAL_IPS']:
            ipbans = User.query.filter_by(last_ip = request.remote_addr, banned = True)
            for ipban in ipbans:
                if datetime.now() < ipban.banexpiration:
                    ban_user(user.id, ipban.banexpiration, ipban.banreason)
                    break

        if user.banned and datetime.now() >= user.banexpiration: # Снятие бана
            user.banned = False
            user.banexpiration = None
            user.banreason = None
            user.rating = 0 # Сброс
            db_session.add(user)
            db_session.commit()
            flush_cached_user(user.id)
        elif app.config['RATING_BAN'] and user.rating < app.config['RATING_BAN']:
            ban_user(user.id, datetime.now() + timedelta(days = 10), u'Бан по сумме голосов (вероятно за идиотизм)')


        if request.cookies.get('admin'):
            import hashlib
            try:
                session['admin'] = (hashlib.md5(dispatch_token(request.cookies.get('admin'))) == app.config['ADMIN_PASS_MD5'])
            except:
                session['admin'] = False

        session['canvote'] = not check_banned() and (user.first_post and user.last_post) and \
                             (datetime.now() - user.first_post >= timedelta(days=7)
                              and (datetime.now() - user.last_post) <= timedelta(days=3)) \
                              and user.rating >= app.config['RATING_CANVOTE']
    else: # Новый юзер
        return redirect(url_for('register'))
        #session['canvote'] = False
        #session['banned'] = False
    refresh_user(user)
    response = make_response(jsonify(result=True))
    response.set_cookie('uid', auth_token(session.get('uid')), max_age=app.config['COOKIES_MAX_AGE'])
    session['refresh_time'] = datetime.now() + timedelta(days=1)
    session.permanent = True
    return response

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def get_safe_url(url):
    import base64
    if not app.config.get('SERVER_NAME') or get_netloc(url) != app.config['SERVER_NAME']:
        return url_for('external_redirect', url=base64.b64encode(url))
    else:
        return url

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
@app.template_filter('ext_urls')
def escape_ext_urls(txt):
    import re
    result = txt
    matches = re.finditer(r'\bhref="(https?://[^"\r\n]*)"', txt)
    for m in matches:
        result = result.replace(m.group(0), 'href=\"%s\"' % get_safe_url(m.group(1)))
    return result

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
@app.template_filter('message')
def render_message(msg):
    #from jinja2 import Markup
    import re
    r = msg
    r = re.sub(r'(?s)\[quote](.*?)\[/quote\]', '<div class="quote">\\1</div>', r)
    r = re.sub(r'(?s)\[spoiler](.*?)\[/spoiler\]', "<a style=\"background:darkgray;color:darkgray\" onmouseover=\"this.style.color=\'white';\" onmouseout=\"this.style.color=\'darkgray\';\">\\1</a>", r)
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
        return jsonify(result=False)
    post = Post.query.filter_by(id = pid).first()
    result = False
    if session.get('canvote') and not check_banned() or session.get('admin'):
        user = get_user(session.get('uid'))
        vote = Vote.query.filter_by(user_id = user.id, post_id = post.id).first()
        if user and post and user.id != post.user_id and not vote and not (val > 1 or val < -1):
            vote = Vote(post_id = post.id, user_id = user.id, value = val)
            post.rating += val
            if app.config['RATING_TRASH'] and post.rating <= app.config['RATING_TRASH']:
                post.section = app.config['TRASH'] # Перенос в помойку
                answers = Post.query.filter_by(parent = post.id)
                for a in answers:
                    a.section = app.config['TRASH']
                    db_session.add(a)
            author = get_user(post.user_id)
            if author:
                author.rating += val
                if app.config['RATING_BAN'] and author.rating < app.config['RATING_BAN']:
                    author.banned = True
                    author.banexpiration = datetime.now() + timedelta(days = 10)
                    author.banreason = u'Бан по сумме голосов (вероятно за идиотизм)'
                    cache.delete_memoized(set_uid)
                db_session.add(author)
            db_session.add(post)
            db_session.add(vote)
            db_session.commit()
            result = True
            flush_cache()

    return jsonify(result = result, post_rating = post.rating)

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


def set_fp_callback(uid, fingerprint):
    session['fingerprint'] = fingerprint
    @cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
    def get_current_user(uid, ip, fp):
        from sqlalchemy import or_
        rec = get_user(uid) if uid else (User.query.filter(or_(User.fingerprint == fp, User.last_ip == ip)).first() if app.config['USER_UNICAL_IPS'] else User.query.filter(User.fingerprint == fp).first())
        if rec is None:
            rec = User(last_ip = ip, last_useragent = request.headers.get('User-Agent'), fingerprint = fp)
            db_session.add(rec)
            db_session.commit()
            flush_cached_user(rec.id)
        return rec

    if not session.get('uid'):
        rec = get_current_user(uid, request.headers.get('X-Forwarded-For') or request.remote_addr, get_current_fingerprint())
        if rec and rec.id:
            set_uid(rec.id)

    return jsonify(result=True, new_id = auth_token(session.get('uid')))


@app.before_request
def user_check():
    session['crawler'] = request.headers.get('User-Agent') and any(_ in request.headers['User-Agent'] for _ in ['Googlebot', '+http://yandex.com/bots', 'Yahoo! Slurp', 'XML-Sitemaps'])
    @cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
    def check_ip(ip):
        return app.config['IP_BLOCKLIST'].InList(ip)

    session.permanent = True
    if not session.get('crawler'):
        if not request.blueprint and request.endpoint not in ['register', 'static', 'flask_util_js']:
            if app.config['RECAPTCHA_ENABLED'] and (not session.get('human-test-validity') or session.get('human-test-validity') < datetime.now()):
                return redirect(url_for('human_test'))
            elif app.config['CAPTCHA_ENABLED'] and (not session.get('captcha-resolve')):
                return redirect(url_for('captcha.show_captcha'))
        if not session.get('uid') and session.get('fingerprint') and (not request.blueprint and request.endpoint not in ['register', 'static','flask_util_js']):
            return redirect(url_for('register'))

        if check_ip(request.headers.get('X-Forwarded-For') or request.remote_addr):
            return render_template('error.html', errortitle=u'Этот IP-адрес заблокирован')

        if session.get('refresh_time') and session.get('uid') and session['refresh_time'] >= datetime.now():
            set_uid(session['uid'])

@cache.cached(timeout=app.config['CACHING_TIMEOUT'])
@app.route('/index')
@app.route('/')
def index():
    return render_template("index.html", sections = app.config['SECTIONS'])


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def sitemap_files():
    from flask import Response
    @cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
    def render_static_template(filename):
        return render_template(filename)
    return Response(render_static_template(request.path[1:]), mimetype = 'text/plain')

def get_page_number(post):
    return post.position / app.config['MAX_POSTS_ON_PAGE'] + (post.position % app.config['MAX_POSTS_ON_PAGE'] > 0) if post.position else 1

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
@app.route('/viewpost/<int:postid>') # Посмотреть пост в треде
def viewpost(postid):
    post = get_posts('post', postid=postid)
    if post:
        if post.parent == 0:
            return redirect(url_for('view', postid = postid))
        else:
            return redirect(url_for('view', postid=post.parent, page=get_page_number(post)) + '#t' + str(postid))

@app.route('/semenodetector/<int:postid>')
@app.route('/semenodetector/<int:postid>/<int:page>')
def semeno_detector(postid, page=1):
    return render_semenodetector(postid, page)

@app.route('/add-to-favorites')
def add_to_favorites():
    thid = int(request.args.get('thid'))
    session['favorites'] = session.get('favorites') or list()
    if thid not in session['favorites']:
        session['favorites'].append(thid)
        return jsonify(result=url_for('static', filename='unfav.png'))
    else:
        session['favorites'].remove(thid)
        return jsonify(result=url_for('static', filename='fav.png'))

@app.route('/unhide-threads')
def unhide_threads():
    session['hidden'] = []
    return jsonify(result=True)

@app.route('/hide-thread')
def hide_thread():
    thid = int(request.args.get('thid'))
    if not session.get('hidden'):
        session['hidden'] = list()
    session['hidden'].append(thid)
    return jsonify(result=True)

@app.route('/mythreads')
@app.route('/mythreads/<int:page>')
def mythreads(page=1):
    return render_mythreads(page)

@app.route('/answers')
@app.route('/answers/<int:page>')
def answers(page=1):
    return render_answers(page)

@app.route('/favorites')
@app.route('/favorites/<int:page>')
def favorites(page=1):
    return render_favorites(page)


@app.route('/view/<int:postid>')
@app.route('/view/<int:postid>/<int:page>')
def view(postid, page=0):
    return render_view(postid, page)

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

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def get_netloc(url):
    import urlparse
    return urlparse.urlparse(url).netloc

#@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
@app.route('/img/<int:randid>/<filename>', methods=['GET'])
def getimage(randid, filename):
    #if not request.headers.get('Referer') or get_netloc(request.headers.get('Referer')).split(':')[0] not in app.config['ALLOWED_HOSTS']:
    #    return send_from_directory('static', 'hotlink.png')
    if int(randid) == 0:
        return send_from_directory(app.config['IMG_FOLDER'], filename)
    else:
        return send_from_directory(os.path.join(app.config['BASE_RANDOMPIC_DIR'], app.config['RANDOM_SETS'][randid]['dir']), filename)

def del_post(post, commit = True): # Рекурсивное удаление поста
    from sqlalchemy import or_
    if post.parent != 0:
        parent = Post.query.filter_by(id = post.parent).first()
        if parent.last_answer == post.time:
            last_post = Post.query.filter(Post.parent == parent.id, Post.id != post.id).order_by(
                        Post.time.desc()).first()
            if last_post:
                parent.last_answer = last_post.time
        parent.answers -= 1
        db_session.add(parent)

    user = get_user(post.user_id)
    if user.last_post == post.time:
        last_post = Post.query.filter(Post.user_id == user.id, Post.id != post.id).order_by(
            Post.time.desc()).first()
        if last_post:
            user.last_post = last_post.time
        else:
            user.last_post = None
        db_session.add(user)
    elif user.first_post == post.time:
        first_post = Post.query.filter(Post.user_id == user.id, Post.id != post.id).order_by(
            Post.time.asc()).first()
        if first_post:
            user.first_post = first_post.time
        else:
            user.first_post = None
        db_session.add(user)

    childs = Post.query.filter(or_(Post.answer_to == post.id, Post.parent == post.id))
    for c in childs:
        del_post(c, False)
    votes = Vote.query.filter_by(post_id = post.id)
    for v in votes:
        db_session.delete(v)
    db_session.commit()

    db_session.delete(post)
    if commit:
        db_session.commit()

    if not Post.query.filter_by(image=post.image).count():
        try:
            import os
            os.remove(os.path.join(app.config['IMG_FOLDER'], post.image))
            os.remove(os.path.join(app.config['IMG_FOLDER'], post.thumb))
        except OSError as e:
            import errno
            if e.errno != errno.ENOENT:
                raise

    flush_cache()

@app.route('/delpost')
def postdel():
    postid = int(request.args.get('postid'))
    post = get_posts('post', postid=postid)
    if not session.get('admin') and (not postid in session.get('can_delete') or not post or post.user_id != int(session.get('uid'))):
        return render_template("error.html", errortitle=u'Ошибка удаления поста')

    del_post(post, True)
    if post.parent == 0:
        return redirect(url_for('section', SectionName=post.section))
    else:
        return redirect(url_for('viewpost', postid=post.parent))

def thread_transfer(thid, new_section):
    post = get_posts('post', postid=thid)

    if post and post.parent == 0:
        post.section = new_section
        db_session.add(post)
        childs = Post.query.filter_by(parent = thid)
        for c in childs:
            c.section = new_section
            db_session.add(c)
        db_session.commit()
        flush_cache()

@app.route('/admin/transfer_data')
def admin_transfer_data():
    from flask import render_template_string
    post = get_posts('post', postid=request.args['thread_id'])
    return render_template_string('''<select id="tsb_{{ post.id }}">
    {% for key, value in config.SECTIONS.iteritems()%}
    <option {% if key == post.section %}selected{% endif %} value="{{ key }}">{{ value }}</option>
    {% endfor %}
    </select>''', post=post)

@app.route('/admin/transfer', methods=['POST'])
def admin_transfer():
    if not session.get('admin'):
        return jsonify(result=False)
    thid = int(request.form['thread_id'])
    newsection = request.form['new_section']
    if app.config['SECTIONS'].get(newsection): # section key is valid
        thread_transfer(thid, newsection)
    return jsonify(result=True)

@app.route('/admin/pin') # Закрепляет на 3 дня
def admin_pin_thread():
    if not session.get('admin'):
        return jsonify(result=False)
    post = get_posts('post', postid=int(request.args['thread_id']))
    post.last_answer = datetime.now() + timedelta(days=3)
    db_session.add(post)
    db_session.commit()
    flush_cache()
    return jsonify(result=True)

@app.route('/admin/unpin')
def admin_unpin_thread():
    if not session.get('admin'):
        return jsonify(result=False)
    post = get_posts('post', postid=int(request.args['thread_id']))
    last_post = Post.query.filter(Post.parent == post.id).order_by(
        Post.time.desc()).first()
    if last_post:
        post.last_answer = last_post.time
        db_session.add(post)
        db_session.commit()
        flush_cache()
    return jsonify(result=True)

@app.route('/admin/clear_cache')
def admin_clear_cache():
    if not session.get('admin'):
        return jsonify(result=False)
    else:
        try:
            cache.clear()
            return jsonify(result=True)
        except:
            return jsonify(result=False)

@app.route('/admin/del_ip')
def admin_delip():
    if not session.get('admin'):
        return jsonify(result=False)

    ip = request.args.get('ipaddr')
    posts = Post.query.filter_by(from_ip = ip)
    for p in posts:
        del_post(p, False)
    users = User.query.filter_by(last_ip = ip)
    for u in users:
        u.banned = True
        u.banexpiration = datetime.now() + timedelta(days = 30)
        u.banreason = u'Забанен модератором по айпи'
        db_session.add(u)

    db_session.commit()
    return jsonify(result=True)

@app.route('/admin/ban')
def admin_ban(userid = 0):
    if userid == 0: userid = int(request.args.get('userid'))

    if not session.get('admin') or userid == session.get('uid'):
        return jsonify(result=False) # Ошибка

    ban_user(userid, datetime.now() + timedelta(days = 30), u'Забанен модератором')
    return jsonify(result=True)

@app.route('/admin/delall')
def admin_delall():
    if not session.get('admin'):
        return jsonify(result=False)
    userid = int(request.args.get('userid'))
    posts = Post.query.filter_by(user_id = userid)
    for p in posts:
        del_post(p, False)
    db_session.commit()
    #print(u'Все посты пользователя %d удалены' % int(userid))
    #return admin_ban(userid)
    return jsonify(result=True)

@app.route('/admin/login')
def admin_login():
    import hashlib
    if (hashlib.md5(request.args.get('p')).hexdigest() == app.config.get('ADMIN_PASS_MD5')) or request.remote_addr == '127.0.0.1':
        session['admin'] = True
    return redirect(redirect_url())

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

    if check_banned():
        user = get_user(session.get('uid'))
        if user and user.banreason:
            return render_template("error.html", errortitle = u"Вы забанены и не можете постить тут.\r\nПричина: %s" \
                                % user.banreason)
        else:
            return render_template("error.html", errortitle = u"Вы забанены и не можете постить тут.")

    form = PostForm()
    if form.validate_on_submit():
        form.msg.data = form.msg.data.strip()
        form.title.data = form.title.data.strip()
        if not len(form.msg.data) and not len(form.img_url.data) and not 'img' in request.files and int(form.parent.data) == 0:
            return render_template("error.html", errortitle = u"Нельзя запостить пустой тред")
        if app.config['SECTIONS'].get(form.section.data) is None:
            return render_template("error.html", errortitle = u"Раздел не найден")

        user = get_user(session.get('uid'))
        if user is None:
            return redirect(url_for('register'))
        if user.banned and (datetime.now() < user.banexpiration):
            return render_template("error.html", errortitle = u"Вы забанены и не можете постить тут: " + user.banreason)

        if not session.get('admin') and user.last_post is not None and (datetime.now() - user.last_post) < timedelta(seconds = 30):
            return render_template("error.html", errortitle = u"Пост можно отправлять не чаще, чем раз в 30 секунд")

        if not session.get('admin') and user.last_post is not None and (datetime.now() - user.last_post) < timedelta(minutes = 3) and form.parent == 0:
            return render_template("error.html", errortitle = u"Треды можно создавать не чаще, чем раз в 3 минуты")

        from jinja2 import Markup
        entry = Post(title = form.title.data, message = unicode(Markup.escape(form.msg.data)), time = datetime.now(), parent = int(form.parent.data), answer_to = int(form.answer_to.data), section = form.section.data, from_ip = request.remote_addr, user_id = user.id, thumb = '', image = '', last_answer = datetime.now())

        if not session.get('admin'):
            msghash = hashlib.md5(entry.message.encode('utf-8')).hexdigest()
            if session.get('last_message_hash') == msghash:
                return render_template("error.html", errortitle=u'Не надо отправлять один и тот же пост несколько раз')
            session['last_message_hash'] = msghash


        parent = Post.query.filter_by(id = entry.parent).first() if entry.parent != 0 else None
        if parent:
            if entry.answer_to != entry.parent:
                answer = Post.query.filter_by(id = entry.answer_to).first()
                if not answer or answer.parent != entry.parent:
                    return render_template("error.html", errortitle = u"Неверные данные")
            if parent:
                entry.position = parent.answers
                parent.answers += 1
                if not form.sage.data and (not parent.last_answer or parent.last_answer < entry.time):
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

        user.last_ip = request.headers.get('X-Forwarded-For') or request.remote_addr
        user.last_useragent = request.headers.get('User-Agent')
        user.last_post = entry.time
        if not user.first_post:
            user.first_post = entry.time

        db_session.add(user)
        db_session.add(entry)
        db_session.commit()

        flush_cache()
        flush_cached_user(user.id)

        session['can_delete'] = session.get('can_delete') or list()
        session['can_delete'].append(entry.id)
        if entry.parent == 0:
            return redirect(url_for('view', postid=entry.id))
        else:
            return redirect(url_for('viewpost', postid=entry.id))
    else:
        for error in form.errors:
                flash(error)
        return render_template("error.html", errortitle=u'Ошибка отправки')


@app.route('/gallery')
@app.route('/gallery/<int:page>')
def gallery(page=1):
    return render_gallery(page)


@app.route('/all')
@app.route('/all/<int:page>')
def allsections(page=1):
    return render_stream(page)


@app.route('/boards/<SectionName>')
@app.route('/boards/<SectionName>/<int:page>')
def section(SectionName, page=1):
    first_post = get_user(session['uid']).first_post
    if app.config['SECTIONS'].get(SectionName) is None or \
            (SectionName in app.config['HIDDEN_BOARDS'] and (not session.get('uid') or session.get('crawler') or not first_post or first_post < datetime.now() + timedelta(hours=3) or check_banned())):
        return render_template("error.html", errortitle = u"Раздел не найден")

    else:
        return render_section(SectionName, page)


# on start
from os import listdir
from os.path import isfile, join
import locale
locale.setlocale(locale.LC_ALL, '')

app.config['IP_BLOCKLIST'] = ipcheck.IpList()
if os.path.exists(app.config['IP_BLOCKLIST_FILE']):
    app.config['IP_BLOCKLIST'].Load(app.config['IP_BLOCKLIST_FILE'])

js = Bundle('jquery-2.0.3.min.js', 'jsfunctions.js', 'images.js',
            filters=(None if app.config['DEBUG_ENABLED'] else 'yui_js'), output='gen/main.js')
css = Bundle('style.css', filters=(None if app.config['DEBUG_ENABLED'] else 'yui_css'), output='gen/main.css')
assets.register('js_main', js)
assets.register('css_main', css)

for r in app.config['RANDOM_SETS']:
    if r.has_key('dir') and os.path.exists(os.path.join(app.config['BASE_RANDOMPIC_DIR'], r.get('dir'))):
        onlyfiles = [ f for f in listdir(os.path.join(app.config['BASE_RANDOMPIC_DIR'], r['dir'])) if isfile(join(os.path.join(app.config['BASE_RANDOMPIC_DIR'], r['dir']), f)) ]
        RANDOM_IMAGES.append(onlyfiles)

from flask.ext.util_js import FlaskUtilJs
fujs = FlaskUtilJs(app)


@app.context_processor
def inject_fujs():
    return dict(fujs=fujs)