# coding:utf-8
# !/usr/bin/env python

import os
from app import create_app, db
from app.models import User, Role
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

# 先创建程序。如果已定义环境变量 LOTUS_CONFIG ，则读取配置名；否则默认配置。
app = create_app(os.getenv('LOTUS_CONFIG') or 'default')

# 初始化 Flask-Script、Flask-Migrate 和为 Python shell 定义的上下文
manager = Manager(app)
migrate = Migrate(app, db)

# fixme
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context()))
manager.add_command('db', MigrateCommand)
print manager.command


# 启动单元测试命令 fixme
@manager.command
def test():
    '''run the unit tests '''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    print manager.command
    print "*" * 10
    manager.run()