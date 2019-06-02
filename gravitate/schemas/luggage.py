# from marshmallow import fields
# from flask_marshmallow import Marshmallow
from flasgger import Schema, fields

# ma = Marshmallow()


class LuggageItemSchema(Schema):
    luggage_type = fields.Str()
    weight_in_lbs = fields.Number()


class LuggageCollectionSchema(Schema):
    luggages = fields.Nested('LuggageItemSchema', many=True)
