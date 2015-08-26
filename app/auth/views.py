# coding:utf-8

from flask import render_template, redirect, url_for, flash
from flask.ext.login import Login_user
from . import auth
from .forms import LoginForm
from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash("Invalida username or password.")
    return render_template('auth/login.html', form=form)


'''
为 render_template() 指定的模板文件保存在 auth 文件夹中。这个文件夹必须在
app/templates 中创建，因为 Flask 认为模板的路径是相对于程序模板文件夹而言的。为避
免与 main 蓝本和后续添加的蓝本发生模板命名冲突，可以把蓝本使用的模板保存在单独的
文件夹中。
'''