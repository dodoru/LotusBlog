# coding:utf-8
'''
generate_password_hash(password, method=pbkdf2:sha1, salt_length=8) ：
这个函数将原始密码作为输入, 以字符串形式输出密码的散列值， 输出的值可保存在用户数据库中。
method 和 salt_length 的默认值就能满足大多数需求。

check_password_hash(hash, password) ：这个函数的参数是从数据库中取回的密码散列
值和用户输入的密码。返回值为 True 表明密码正确。

Flask-Login要求实现的用户方法
方法 说明
is_authenticated() 如果用户已经登录，必须返回 True ，否则返回 False
is_active() 如果允许用户登录，必须返回 True ，否则返回 False 。如果要禁用账户，可以返回 False
is_anonymous() 对普通用户必须返回 False
get_id() 必须返回用户的唯一标识符，使用 Unicode 编码字符串
'''

from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import bootstrap, db, moment, mail
from . import login_manager


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(20),unique=True,index=True)
    username=db.Column(db.String(20),unique=True,index=True)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    role=db.relationship('Role',backref='users')
        # ...
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute. ')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    pass

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def test():
    u = User()
    u.password = 'cat'
    print u.password_hash


if __name__ == '__main__':
    test()

