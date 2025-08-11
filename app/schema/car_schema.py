from app.extensions import ma
from marshmallow import fields, validate, validates_schema, ValidationError

class CarSchema(ma.Schema):
    ID_KEY = 'id'
    CAR_ID_KEY = 'car_id'
    NAME_KEY = 'name'
    MAKE_KEY = 'make'
    MODEL_KEY = 'model'
    YEAR_KEY = 'year'
    CREATED_AT_KEY = 'created_at'

    id = fields.Int(dump_only=True)
    car_id = fields.Str(required=True, validate=validate.Length(min=1))
    name = fields.Str(required=True, validate=validate.Length(min=1))
    make = fields.Str(required=True, validate=validate.Length(min=1))
    model = fields.Str(required=True, validate=validate.Length(min=1))
    year = fields.Int(required=True, validate=validate.Range(min=1900, max=2100))
    created_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_fields(self, data, **kwargs):
        for field_name in ['car_id', 'name', 'make', 'model']:
            if data.get(field_name, "").strip() == "":
                raise ValidationError(f"{field_name} cannot be empty or just spaces.")

car_schema = CarSchema()
cars_schema = CarSchema(many=True)

