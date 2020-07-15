from app import ma
from marshmallow import fields, validate

class TodoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id', 'name', 'year', 'month', 'week', 'day', 'finished')

class ClientSchema(ma.Schema):
    client_name = fields.String(required=True)
    client_uri = fields.String(required=True)
    grant_types = fields.List(fields.String(), validate=validate.Length(min=1))
    redirect_uris = fields.List(fields.String(), validate=validate.Length(min=1))
    response_types = fields.List(fields.String(), validate=validate.Length(min=1))
    scope = fields.String(required=True)
    token_endpoint_auth_method = fields.String()

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

client_schema = ClientSchema()