from marshmallow import fields
from app.extensions import ma


class UserSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)


class UserResponseSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    token = fields.Str(dump_only=True)


class UserLoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)


user_schema = UserSchema()
user_response_schema = UserResponseSchema()
user_login_schema = UserLoginSchema()
