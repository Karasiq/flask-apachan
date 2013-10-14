# coding=utf-8
from app import *

@cache.memoize(timeout=3600)
def render_stream(page, session=session, config=app.config):
    posts = Post.query.filter_by(parent = 0).order_by(Post.last_answer.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    form = PostForm()
    form.parent.data = '0'
    form.section.data = 'b'
    return render_template("section.html", SecName = u'Поток', posts = posts, form = form,
                           randoms = app.config['RANDOM_SETS'], show_section = True,
                           baseurl = '/all/')


@cache.memoize(timeout=3600)
def render_section(SectionName, page, session=session, config=app.config):
    posts = Post.query.filter_by(parent = 0, section = SectionName).order_by(Post.last_answer.desc()).paginate(page, per_page=app.config['MAX_POSTS_ON_PAGE'])
    form = PostForm()
    form.section.data = SectionName
    return render_template("section.html", SecName = app.config['SECTIONS'][SectionName], posts = posts, form = form, randoms = app.config['RANDOM_SETS'], baseurl = '/boards/%s/' % SectionName)

@cache.memoize(timeout=3600)
def render_view(postid, page, session=session, config=app.config):
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