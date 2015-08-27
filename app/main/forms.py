# coding:utf-8
# 为了完全修改程序的页面，表单对象也要移到蓝本中，保存于 app/main/forms.py 模块。

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(Form):
    nickname = SubmitField('What is your name? ', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    nickname = StringField('Real name', validators=[Length(0, 64)])
    lacation = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = StringField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField()

