from app.extensions import ma
from marshmallow import fields, validate

class UserSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))

    def to_json(self, user):
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }

    class Meta:
        fields = ("id", "username", "email", "password")


user_schema = UserSchema()

user_response_schema = UserSchema(exclude=["password"])


class UserRequestSchema(UserSchema):
    class Meta:
        exclude = ("id",)


class UserResponseSchema(UserSchema):
    class Meta:
        exclude = ("password",)
