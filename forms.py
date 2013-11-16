# coding=utf-8
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, FileField, HiddenField, BooleanField, SelectField, SubmitField
from flask.ext.wtf.recaptcha import RecaptchaField
from wtforms.validators import Required, Length
from config import RANDOM_SETS

class HumanTestForm(Form):
    captcha = RecaptchaField()

class PostForm(Form):
    title = TextField('title', validators = [Length(max = 50)])
    msg = TextAreaField('msg', validators = [Length(max = 5000)])
    img_url = TextField('img_url', validators = [Length(max = 300)])
    img = FileField('img')
    sage = BooleanField('sage', default=False)
    parent = HiddenField('parent', default='0')
    answer_to = HiddenField('answer_to', default='0')
    section = HiddenField('section')

    choices = [(str(RANDOM_SETS.index(r)), '%s (%d)' % (r.get('name'), RANDOM_SETS.index(r))) for r in RANDOM_SETS]
    ins_random = SelectField('ins_random', choices=choices, default=0)
    commit = SubmitField('commit')