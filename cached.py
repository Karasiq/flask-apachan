# coding=utf-8
# Views file
from app import *

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def get_user(uid):
    return User.query.filter_by(id=uid).first()

def get_posts(e, page = 1, postid = None, idlist = None, userid = None, section = app.config['DEFAULT_SECTION']):
    from sqlalchemy import not_, and_, or_
    if e == 'stream' or e == 'allsections':
        return Post.query.filter( and_(Post.parent == 0, not_(Post.section.in_(app.config['HIDDEN_BOARDS']))) ).order_by(Post.last_answer.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    elif e == 'post':
        return Post.query.filter_by(id = postid).first()
    elif e == 'thread' or e == 'view':
        posts = Post.query.filter(or_(Post.parent == postid, Post.answer_to == postid), Post.id != postid)
        if page == 0: page = posts.count() / app.config['MAX_POSTS_ON_PAGE'] + (posts.count() % app.config['MAX_POSTS_ON_PAGE'] > 0 or posts.count() == 0)
        return posts.order_by(Post.id.asc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    elif e == 'section':
        return Post.query.filter_by(parent = 0, section = section).order_by(Post.last_answer.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    elif e == 'selection' or e == 'favorites':
        return Post.query.filter(Post.id.in_(idlist)).order_by(Post.id.asc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE']) if idlist else None
    elif e == 'user_posts':
        if not userid: userid = session.get('uid')
        return Post.query.filter_by(user_id = userid)
    elif e == 'user_threads' or e == 'mythreads':
        if not userid: userid = session.get('uid')
        return Post.query.filter_by(user_id = userid, parent = 0).order_by(Post.id.asc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    elif e == 'user_answers' or e == 'answers':
        if not userid: userid = session.get('uid')
        posts = get_posts('user_posts', userid=userid).order_by(Post.id.desc()).limit(100)
        return Post.query.filter(Post.answer_to.in_(id_list(posts))).order_by(Post.time.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    elif e == 'detector' or e == 'semeno_detector':
        post = get_posts('post', postid=postid)
        if post:
            parent_id = post.parent if post.parent != 0 else post.id
            return Post.query.filter_by(parent = parent_id, user_id = post.user_id).order_by(Post.id.asc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
        else:
            return None
    elif e == 'gallery':
        return Post.query.filter(Post.randid == 0, Post.image != '').order_by(Post.time.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def render_stream(page, session=session):
    posts = get_posts('stream', page)
    form = PostForm()
    form.parent.data = '0'
    form.section.data = app.config['DEFAULT_SECTION']
    return render_template("section.html", SecName = u'Поток', posts = posts, form = form,
                           randoms = app.config['RANDOM_SETS'], show_section = True,
                           baseurl = '/all/')


@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def render_section(SectionName, page, session=session):
    posts = get_posts('section', page, section=SectionName)
    form = PostForm()
    form.section.data = SectionName
    return render_template("section.html", SecName = app.config['SECTIONS'][SectionName], posts = posts, form = form, randoms = app.config['RANDOM_SETS'], baseurl = '/boards/%s/' % SectionName, section = SectionName)

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def render_view(postid, page, session=session):
    from app import check_banned, get_first_post_time
    post = get_posts('post', postid=postid)
    answers = get_posts('thread', page, postid)

    first_post = get_first_post_time()
    if post is None or \
            (post.section in app.config['HIDDEN_BOARDS'] and (not session.get('uid') or session.get('crawler') or not first_post or datetime.now() - first_post < timedelta(hours=3) or check_banned()) and not session.get('admin')):
        return render_template("error.html", errortitle = u"Пост не найден")
        
    form = PostForm()
    form.answer_to.data = post.id
    if int(post.parent) == 0:
        form.parent.data = post.id
    else:
        form.parent.data = post.parent
    form.section.data = post.section

    return render_template("section.html", SecName = app.config['SECTIONS'][post.section], posts = answers, form = form, mainpost = post, randoms = app.config['RANDOM_SETS'], baseurl = '/view/%d/' % postid, page_posts = id_list(answers.items))

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def render_favorites(page, session=session):
    if session.get('favorites'):
        posts = get_posts('selection', idlist=session['favorites'])
        return render_template("section.html", SecName = u'Избранное', posts = posts,
                               randoms = app.config['RANDOM_SETS'], baseurl = '/favorites/',
                               page_posts = id_list(posts.items))
    else:
        return render_template('error.html', errortitle=u'В избранном ничего нет')

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def render_answers(page, session=session):
    answers = get_posts('user_answers', page, userid=session.get('uid'))
    return render_template("section.html", SecName = u'Ответы', posts = answers,
                           randoms = app.config['RANDOM_SETS'], baseurl = '/answers/',
                           page_posts = id_list(answers.items), show_answer_to = True)

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def render_mythreads(page, session=session):
    posts = get_posts('user_threads', page, userid=session.get('uid'))
    return render_template("section.html", SecName = u'Мои треды', posts = posts, randoms = app.config['RANDOM_SETS'], page_posts = id_list(posts.items), baseurl = '/mythreads/')

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def render_semenodetector(postid, page, session=session):
    posts = get_posts('detector', page, postid = postid)
    return render_template("section.html", SecName = u'Семенодетектор (#%s)' % int(postid), posts = posts, randoms = app.config['RANDOM_SETS'], baseurl = '/semenodetector/%d/' % postid, page_posts = id_list(posts.items))

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def render_gallery(page, session=session):
    posts = get_posts('gallery', page)
    return render_template("gallery.html", posts = posts, baseurl = '/gallery/')

@cache.memoize(timeout=app.config['CACHING_TIMEOUT'])
def render_ajax(data, session=session):
    mainpost = get_posts('post', postid=int(data['postid'])) if data.get('postid') else None
    posts = get_posts(data['endpoint'], page=int(data['page']) if data.get('page') else 1, postid=int(data['postid']) if data.get('postid') else None, section=data.get('section'))
    return jsonify(result = True, posts = render_template("posts.html", mainpost = mainpost, posts = posts, baseurl = data['baseurl'], show_section = data.get('show_section'), show_answer_to = data.get('show_answer_to'), page_posts = id_list(posts.items)))

def flush_cached_user(uid):
    cache.delete_memoized(get_user, int(uid))
    cache.delete_memoized(get_user, long(uid))

def flush_cache():
    from app import viewpost
    # cache.delete_memoized(get_user)
    cache.delete_memoized(render_ajax)
    cache.delete_memoized(viewpost)
    cache.delete_memoized(render_view)
    cache.delete_memoized(render_section)
    cache.delete_memoized(render_stream)
    cache.delete_memoized(render_gallery)
    cache.delete_memoized(render_answers)
    cache.delete_memoized(render_mythreads)
    cache.delete_memoized(render_semenodetector)
    return True