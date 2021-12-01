import datetime
from operator import pos
from typing import NewType

from flask import abort, current_app, jsonify
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from webapp.blog.models import db, Post, Tag, Reminder
from webapp.auth.models import User
from .parsers import(
    post_get_parser,
    post_post_parser,
    post_put_parser,
    reminder_post_parser
)
from .fields import HTMLField

nested_tag_fields = {
    'id': fields.Integer(),
    'title': fields.String()
}

post_fields ={
    'id': fields.Integer(),
    'author':fields.String(attribute=lambda x:x.user.username),
    'title': fields.String(),
    'text': HTMLField(),
    'tags': fields.List(fields.Nested(nested_tag_fields)),
    'publish_date': fields.DateTime(dt_format='iso8601')
}

remider_fields = {
    'id': fields.Integer(),
    'email': fields.String(),
    'text': fields.String()
}

def add_tags_to_post(post, tag_list):
    for item in tag_list:
        tag = Tag.query.filter_by(title=item).first()
        if tag:
            post.tags.append(tag)
        else:
            new_tag = Tag(item)
            post.tags.append(new_tag)

class PostApi(Resource):
    @marshal_with(post_fields)
    @jwt_required
    def get(self, post_id=None):
        if post_id:
            post = Post.query.get(post_id)
            if not post:
                abort(404)
            return post
        else:
            args = post_get_parser.parse_args()
            page = args['page'] or 1

            if args['user']:
                user = User.query.filter_by(username=args['user']).first()
                if not user:
                    abort(404)

                posts = user.posts.order_by(
                    Post.publish_date.desc()
                ).paginate(page, current_app.config['POST_PER_PAGE'])
            else:
                posts = Post.quey.order_by(
                    Post.publish_date.desc()
                ).paginate(page, current_app.config['POST_PER_PAGE'])
            
            return posts.items

    