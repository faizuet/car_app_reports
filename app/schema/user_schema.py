from app.extensions import ma
from marshmallow import fields, validate

class UserSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=6)
    )

class UserRequestSchema(UserSchema):
    class Meta:
        exclude = ("id",)

class UserResponseSchema(ma.Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()

class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

class UserUpdateSchema(ma.Schema):
    username = fields.Str(validate=validate.Length(min=3))
    email = fields.Email()
    password = fields.Str(load_only=True, validate=validate.Length(min=6))

    class Meta:
        fields = ("username", "email", "password")

user_schema = UserSchema()
user_request_schema = UserRequestSchema()
user_response_schema = UserResponseSchema()
login_schema = LoginSchema()
user_update_schema = UserUpdateSchema()

