# coding:utf-8


# Python 的 unittest 包编写测试, https://docs.python.org/2/library/unittest.html）
import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    # 尝试创建一个测试环境
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # 删除数据库和程序上下文
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # 测试确保程序实例存在
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    # 测试确保程序在测试配置中运行
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

