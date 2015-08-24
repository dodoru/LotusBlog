# coding:utf-8

from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager=LoginManager
login_manager.session_protection='strong'
login_manager.login_view='auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)

    # @errorhandler()
    '''
程序的路由保存在包里的 app/main/views.py 模块中，而错误处理程序保存在 app/main/
errors.py 模块中。导入这两个模块就能把路由和错误处理程序与蓝本关联起来。注意，这
些模块在 app/main/__init__.py 脚本的末尾导入，这是为了避免循环导入依赖，因为在
views.py 和 errors.py 中还要导入蓝本 main 。
    '''
    # ...
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    '''
    注册蓝本时使用的 url_prefix 是可选参数。如果使用了这个参数，注册后蓝本中定义的
所有路由都会加上指定的前缀，即这个例子中的 /auth。例如，/login 路由会注册成 /auth/
login，在开发 Web 服务器中，完整的 URL 就变成了 http://localhost:5000/auth/login。
    '''

    return app