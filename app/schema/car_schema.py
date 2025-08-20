from marshmallow import fields
from app.extensions import ma

class MakeSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class CarModelSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    make_id = fields.Int()

class CarSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    year = fields.Int()
    category = fields.Str()
    make = fields.Nested(MakeSchema)
    model = fields.Nested(CarModelSchema)

class CarCreateSchema(ma.Schema):
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year = fields.Int(required=True)
    category = fields.Str()

class CarUpdateSchema(ma.Schema):
    make = fields.Str()
    model = fields.Str()
    year = fields.Int()
    category = fields.Str()

