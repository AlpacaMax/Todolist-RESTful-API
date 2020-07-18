from app import ma
from .models import User
from marshmallow import fields, validate, ValidationError, validates

class UserSchema(ma.Schema):
    id = fields.Integer()
    username = fields.String()
    todos = fields.List(fields.Nested(lambda: TodoSchema(exclude=("user",))))

class TodoSchema(ma.Schema):
    id = fields.Integer(load_only=True)
    user = fields.Nested(UserSchema(exclude=("todos",)), dump_only=True)
    name = fields.String(required=True)
    year = fields.Integer(required=True)
    month = fields.Integer(required=True, validate=validate.Range(min=1, max=12))
    week = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    day = fields.Integer(required=True, validate=validate.Range(min=1, max=31))
    finished = fields.Bool(required=True, default=False)

class ClientSchema(ma.Schema):
    client_name = fields.String(required=True)
    client_uri = fields.String(required=True)
    grant_types = fields.List(fields.String(), validate=validate.Length(min=1))
    redirect_uris = fields.List(fields.String(), validate=validate.Length(min=1))
    response_types = fields.List(fields.String(), validate=validate.Length(min=1))
    scope = fields.String(required=True)
    token_endpoint_auth_method = fields.String()

class UserRegisterSchema(ma.Schema):
    username = fields.String(required=True, validate=validate.Length(min=6, max=20))
    password = fields.String(required=True, validate=validate.Length(min=8, max=20))

    @validates("username")
    def is_user_exist(self, value):
        user = User.query.filter(User.username==value).first()
        if (user):
            raise ValidationError("Username is taken!")

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)
client_schema = ClientSchema()
user_register_schema = UserRegisterSchema()
user_schema = UserSchema()