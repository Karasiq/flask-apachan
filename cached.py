# coding=utf-8
from app import *

@cache.memoize(timeout=3600)
def render_stream(page, session=session):
    posts = Post.query.filter_by(parent = 0).order_by(Post.last_answer.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    form = PostForm()
    form.parent.data = '0'
    form.section.data = 'b'
    return render_template("section.html", SecName = u'Поток', posts = posts, form = form,
                           randoms = app.config['RANDOM_SETS'], show_section = True,
                           baseurl = '/all/')


@cache.memoize(timeout=3600)
def render_section(SectionName, page, session=session):
    posts = Post.query.filter_by(parent = 0, section = SectionName).order_by(Post.last_answer.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    form = PostForm()
    form.section.data = SectionName
    return render_template("section.html", SecName = app.config['SECTIONS'][SectionName], posts = posts, form = form, randoms = app.config['RANDOM_SETS'], baseurl = '/boards/%s/' % SectionName)

@cache.memoize(timeout=3600)
def render_view(postid, page, session=session):
    from sqlalchemy import or_
    post = Post.query.filter_by(id = postid).first()
    answers = Post.query.filter(or_(Post.parent == postid, Post.answer_to == postid)).order_by(Post.id.asc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])

    if post is None:
        return render_template("error.html", errortitle = u"Пост не найден")
    form = PostForm()
    form.answer_to.data = post.id
    if int(post.parent) == 0:
        form.parent.data = post.id
    else:
        form.parent.data = post.parent
    form.section.data = post.section

    return render_template("section.html", SecName = app.config['SECTIONS'][post.section], posts = answers, form = form, mainpost = post, randoms = app.config['RANDOM_SETS'], baseurl = '/view/%d/' % postid, page_posts = id_list(answers.items))

@cache.memoize(timeout=3600)
def render_favorites(page, session=session):
    if session.get('favorites'):
        posts = Post.query.filter(Post.id.in_(session['favorites'])).order_by(Post.id.asc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
        return render_template("section.html", SecName = u'Избранное', posts = posts,
                               randoms = app.config['RANDOM_SETS'], baseurl = '/favorites/',
                               page_posts = id_list(posts.items))
    else:
        return render_template('error.html', errortitle=u'В избранном ничего нет')

@cache.memoize(timeout=3600)
def render_answers(page, session=session):
    def get_answers(user_id):
        if user_id:
            posts = Post.query.filter_by(user_id = user_id).order_by(Post.time.desc()).limit(100)
            return Post.query.filter(Post.answer_to.in_(id_list(posts))).order_by(Post.time.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE']) if posts else None
        else:
            return None

    answers = get_answers(session.get('uid'))
    return render_template("section.html", SecName = u'Ответы', posts = answers,
                           randoms = app.config['RANDOM_SETS'], baseurl = '/answers/',
                           page_posts = id_list(answers.items), show_answer_to = True)

@cache.memoize(timeout=3600)
def render_mythreads(page, session=session):
    posts = Post.query.filter(Post.user_id == session['uid'], Post.parent == 0).order_by(Post.last_answer.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE']) if session.get('uid') else None
    return render_template("section.html", SecName = u'Мои треды', posts = posts, randoms = app.config['RANDOM_SETS'], page_posts = id_list(posts.items))

@cache.memoize(timeout=3600)
def render_semenodetector(postid, page, session=session):
    def detect_same_person(post_id):
        post = Post.query.filter_by(id = post_id).first()
        if post:
            parent_id = post.parent if post.parent != 0 else post.id
            return post, Post.query.filter(Post.user_id == post.user_id, Post.parent == parent_id, Post.id != post_id).order_by(Post.id.asc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
        else:
            return None

    post, posts = detect_same_person(postid)
    form = PostForm()
    form.answer_to.data = postid
    if int(post.parent) == 0:
        form.parent.data = post.id
    else:
        form.parent.data = post.parent
    form.section.data = post.section
    return render_template("section.html", SecName = u'Семенодетектор (#%s)' % int(postid), posts = posts, form = form, mainpost = post, randoms = app.config['RANDOM_SETS'], baseurl = '/semenodetector/%d/' % postid, page_posts = id_list(posts.items))

@cache.memoize(timeout=3600)
def render_gallery(page, session=session):
    posts = Post.query.filter(Post.randid == 0, Post.image != '').order_by(Post.last_answer.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    return render_template("gallery.html", posts = posts, baseurl = '/gallery/')

def flush_cache():
    cache.delete_memoized(viewpost)
    cache.delete_memoized(render_view)
    cache.delete_memoized(render_section)
    cache.delete_memoized(render_stream)
    cache.delete_memoized(render_gallery)
    cache.delete_memoized(render_answers)
    cache.delete_memoized(render_mythreads)
    cache.delete_memoized(render_semenodetector)
    return True