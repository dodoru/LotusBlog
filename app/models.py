# coding:utf-8

"""
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
"""

import hashlib
import bleach
from flask import current_app, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymouseUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from markdown import markdown
from datetime import datetime

from . import bootstrap, db, moment, mail
from . import login_manager


class Permission():
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter(Role.name == r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return u'<Role {0}>'.format(self.name)


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, index=True)
    username = db.Column(db.String(20), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # role=db.relationship('Role',backref='users')
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    nickname = db.Column(db.String(20))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow())
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('POST', backref='author', lazy='dynamic')

    # followed 和 followers 关系都定义为单独的一对多关系,
    # 可选参数 foreign_keys 消除外键间的歧义
    # db.backref() 参数并不是指定这两个关系之间的引用关系，而是回引 Follow 模型
    # joined 实现立即从联结查询中加载相关对象
    # dynamic ，关系属性不会直接返回记录，返回查询对象，执行查询之前还可以添加额外的过滤器
    # cascade 参数配置在父对象上执行的操作对相关对象的影响,将用户添加到数据库会话后，要自动把所有关系的对象都添加到会话中。
    # cascade 删除对象时，默认把对象联接的所有相关对象的外键设为空值,
    # delete-orphan ,在关联表中 ,删除记录后,把指向该记录的实体也删除，因为这样能有效销毁联接。

    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all,delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    # 添加到 User 模型和 Post 模型中的类方法，用来生成虚拟数据。
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     nickname=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.qurey.all():
            if not user.is_following(user):
                user.followers(user)
                db.session.add(user)
                db.session.commit()


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # fixme
        if self.role is None:
            if self.email == current_app.config['LOTUS_ADMIN']:
                self.role = Role.query.filter(Role.permissions == 0xff).first()
            if self.role is None:
                self.role = Role.query.filter(Role.default == True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))


    # todo
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute. ')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm_id': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm_id') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generator_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'reset_id': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset_id') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'change_email_id': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email_id') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter(User.email == new_email).first():
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return True

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://secure.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{0}/{1}?s={2}&d={3}&r={4}'.format(url, hash, size, default, rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.query.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    def __repr__(self):
        return '<User {0}, {1}>'.format(self.username, self.email)


# fixme
class AnonymousUser(AnonymouseUserMixin):
    pass


class Post():
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

