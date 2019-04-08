from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


post_tag = db.Table('post_tag',
db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)
followers = db.Table('followers',
db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),
db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


@login.user_loader                      # передача юзера в flask_login бо він не працює з БД
def load_user(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), index = True, unique = True)
    email = db.Column(db.String(124), index = True, unique=True)
    password_hash = db.Column(db.String(256))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')

    followed = db.relationship('User',
    secondary=followers,
    primaryjoin=(followers.c.follower_id == id),
    secondaryjoin=(followers.c.followed_id == id),
    backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')



    def avatar(self, size=100):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def follow(self, username):
        if not self.already_followed(username):
            self.followed.append(username)
            db.session.commit()

    def unfollow(self, username):
        if self.already_followed(username):
            self.followed.remove(username)
            db.session.commit()

    def already_followed(self, username):
        return self.followed.filter(followers.c.followed_id==username.id).count()>0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.date.desc())

    def __repr__(self):
        return '<user id : {}, name : {}>.'.format(self.id, self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text())
    date = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    tags = db.relationship('Tag', secondary=post_tag, backref = db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return '<post id: {} post tags: {} user: {}>'.format(self.id, self.tags, self.user_id)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(128), unique = True)
