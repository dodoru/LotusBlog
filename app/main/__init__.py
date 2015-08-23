# coding:utf-8

from flask import Blueprint

'''

通过实例化一个 Blueprint 类对象可以创建蓝本。这个构造函数有两个必须指定的参数：
蓝本的名字和蓝本所在的包或模块。和程序一样，大多数情况下第二个参数使用 Python 的
__name__ 变量即可。

'''
main = Blueprint('main', __name__)
'''

create_app() 函数就是程序的工厂函数，接受一个参数，是程序使用的配置名。
配置类在 config.py 文件中定义，其中保存的配置可以使用 Flask
app.config 配置对象提供的 from_object() 方法直接导入程序。
至于配置对象，则可以通过名字从 config 字典中选择。
'''

from . import views, errors