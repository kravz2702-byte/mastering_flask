from enum import unique
from operator import index
from os import name
from flask import Flask
from sqlalchemy.orm import backref
from config import DevConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
from sqlalchemy import func
from sqlalchemy.sql import text





app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

def sidebar_data():
    recent = Post.query.order_by(
        Post.publish_date.desc()
    ).limit.all()
    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
        ).join(
            tags
        ).group_by(Tag).order_by(text('total DESC')).limit(5).all()
    return recent, top_tags

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255))
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, username):
        self.username = username
    
    def __repr__(self):
        return "<User {}>".format(self.username)


tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', name='post_tag_id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', name='tag_post_id'))
)

class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text)
    publish_date = db.Column(db.DateTime(), default=datetime.datetime.now)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', name='user_post'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = db.relationship('Tag',
    secondary=tags,
    backref=db.backref('posts', lazy='dynamic')
    )

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)

class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)

    def __init__(self, title):
        self.title = title

    def __repr__(self, title):
        return "<Post '{}'>".format(self.title)

class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text())
    date = db.Column(db.DateTime(), default=datetime.datetime.now)
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id', name='comment_post'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])

# Changed to show the git diff command
@app.route('/')
def home():
    return '<h1>Hello world</h1>'

@app.template_filter
def count_substring(string, sub_string): return string.count(sub_string)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
