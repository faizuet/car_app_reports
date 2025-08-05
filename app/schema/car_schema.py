from app.extensions import ma
from marshmallow import fields, validate

class CarSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    parse_id = fields.Str(required=True, validate=validate.Length(min=1))
    name = fields.Str(dump_only=True)  # auto-generated from make+model if you do that
    make = fields.Str(required=True, validate=validate.Length(min=1))
    model = fields.Str(required=True, validate=validate.Length(min=1))
    year = fields.Int(required=True, validate=validate.Range(min=1900, max=2100))
    created_at = fields.DateTime(dump_only=True)

car_schema = CarSchema()
cars_schema = CarSchema(many=True)
