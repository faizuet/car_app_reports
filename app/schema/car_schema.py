from app.extensions import ma
from marshmallow import fields, validate, validates_schema, ValidationError


class CarModelSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    model_name = fields.Str(required=True, validate=validate.Length(min=1))
    trim = fields.Str()
    year = fields.Int(validate=validate.Range(min=1900, max=2100))

    @validates_schema
    def validate_model_name(self, data, **kwargs):
        if data.get("model_name", "").strip() == "":
            raise ValidationError("model_name cannot be empty or just spaces.")


class CarSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    car_id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    make = fields.Str(required=True, validate=validate.Length(min=1))
    year = fields.Int(required=True, validate=validate.Range(min=1900, max=2100))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    models = fields.List(fields.Nested(CarModelSchema), required=False)

    @validates_schema
    def validate_fields(self, data, **kwargs):
        for field_name in ["name", "make"]:
            if data.get(field_name, "").strip() == "":
                raise ValidationError(f"{field_name} cannot be empty or just spaces.")

