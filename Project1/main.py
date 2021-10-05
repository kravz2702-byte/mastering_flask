from enum import unique
from operator import index
from os import name
from flask import Flask, flash, render_template, redirect, url_for
from flask.json import tag
from sqlalchemy.orm import backref
from config import DevConfig
from flask_sqlalchemy import SQLAlchemy, model
from flask_migrate import Migrate
from flask_wtf import FlaskForm as Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
import datetime
from sqlalchemy import func
from sqlalchemy.sql import text
from flask import Flask, render_template




app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

def sidebar_data():
    recent = Post.query.order_by(
        Post.publish_date.desc()
    ).limit(5).all()
    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
        ).join(
            tags
        ).group_by(Tag).order_by(text('total DESC')).limit(5).all()
    return recent, top_tags

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, username=""):
        self.username = username

    def __repr__(self):
        return '<User {}>'.format(self.username)


tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', name='post_tag_id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', name='tag_post_id'))
)

class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )
    tags = db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
    )

    def __init__(self, title=""):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)

class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)

    def __init__(self, title=""):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)

class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text())
    date = db.Column(db.DateTime(), default=datetime.datetime.now)
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id', name='comment_post'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])

class CommentForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    text = TextAreaField(u'Comment', validators=[DataRequired()])

# Changed to show the git diff command
@app.route('/')
@app.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page,
    app.config['POSTS_PER_PAGE'], False)
    recent, top_tags = sidebar_data()

    return render_template(
        'home.html',
        posts=posts,
        recent=recent,
        top_tags = top_tags
    )

@app.route('/post/<int:post_id>', methods=('GET', 'POST'))
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        try:
            db.session.add(new_comment)
            db.session.commit()
        except Exception as e:
            flash('Error adding your comment: %s' % str(e), 'error')
            db.session.rollback()
        else:
            flash('Comment added', 'info')
        return redirect(url_for('post', post_id=post_id))

    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'post.html',
        post=post,
        tags=tags,
        comments=comments,
        recent=recent,
        top_tags=top_tags,
        form=form
    )
    
@app.route('/posts_by_user/<string:username>')
def posts_by_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'user.html',
        user=user,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )


@app.route('/posts_by_tag/<string:tag_name>')
def posts_by_tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'tag.html',
        tag=tag,
        posts=posts,
        top_tags=top_tags,
        recent=recent
    )

from flask.views import View

class GenericListView(View):

    def __init__(self, model, list_template='generic_list.html'):
        self.model=model
        self.list_template = list_template
        self.columns = self.model.__mapper__.columns.keys()

        super(GenericListView, self).__init__()

    def render_template(self, context):
        return render_template(self.list_template, **context)

    def get_objects(self):
        return self.model.query.all()

    def dispatch_request(self):
        context = {
            'objects' : self.get_objects(),
            'columns' : self.columns}
        return self.render_template(context)

app.add_url_rule(
    '/generic_posts', view_func=GenericListView.as_view(
        'generic_posts', model=Post)
)

app.add_url_rule(
    '/generic_users', view_func=GenericListView.as_view(
        'generic_users', model=User)
)

app.add_url_rule(
    '/generic_comments', view_func=GenericListView.as_view(
        'generic_comments', model=Comment)
)

if __name__ == '__main__':
    app.run( debug=True)
