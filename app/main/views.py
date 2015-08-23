# coding:utf-8

from datetime import datetime
from flask import render_template, session, redirect, url_for, flash

from . import main
from .forms import NameForm
from .. import db
from ..models import User

# diff:路由修饰器由蓝本提供；
@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # ...
        '''
        # Flask 会为蓝本中的全部端点加上一个命名空间，
        # 这样就可以在不同的蓝本中使用相同的端点名定义视图函数，而不会产生冲突。
        # 命名空间就是蓝本的名字（ Blueprint 构造函数的第一个参数） ，
        # 所以视图函数 index() 注册的端点名是 main.index ，
        # 其 URL 使用 url_for('main.index') 获取。在蓝本中可以省略蓝本名，例如 url_for('.index') 。
        同一蓝本中的重定向可使用简写，命名空间是当前请求所在的蓝本.跨蓝本的重定向必须使用带有命名空间的端点名。
        '''
        return redirect(url_for('.index'))
    return render_template('index.html', form=form,
                           name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())

