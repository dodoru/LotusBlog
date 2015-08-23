# coding:utf-8

from flask import render_template
from . import auth


@auth.route('/login')
def login():
    return render_template('auth/login.html')


'''
为 render_template() 指定的模板文件保存在 auth 文件夹中。这个文件夹必须在
app/templates 中创建，因为 Flask 认为模板的路径是相对于程序模板文件夹而言的。为避
免与 main 蓝本和后续添加的蓝本发生模板命名冲突，可以把蓝本使用的模板保存在单独的
文件夹中。
'''