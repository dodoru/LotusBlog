# coding:utf-8
# 为了完全修改程序的页面，表单对象也要移到蓝本中，保存于 app/main/forms.py 模块。

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(Form):
    nickname = SubmitField('What is your name? ', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    nickname = StringField('Nickname', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = StringField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(), Length(1, 64),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                          'Username must begin with a letter')])
    comfirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    nickname = StringField('Nickname', validators=[Length(0, 30)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me...')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. ')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(usernama=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    body = PageDownField("Post your ideas ", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')