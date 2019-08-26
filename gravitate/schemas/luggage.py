# from marshmallow import fields
# from flask_marshmallow import Marshmallow
from flasgger import Schema, fields

# ma = Marshmallow()


class LuggageItemSchemaOld(Schema):
    luggage_type = fields.Str()
    weight_in_lbs = fields.Number()


class LuggageCollectionSchemaOld(Schema):
    luggages = fields.Nested('LuggageItemSchemaOld', many=True)
