from flask_boiler import serializable, schema, fields

Schema = schema.Schema


class LuggageItemSchema(Schema):
    luggage_type = fields.Str(load_from="luggage_type", dump_to="luggage_type")
    weight_in_lbs = fields.Integer(load_from="weight_in_lbs", dump_to="weight_in_lbs")


class LuggageCollectionSchema(Schema):
    luggages = fields.Nested('LuggageItemSchema', many=True, load_from="luggages", dump_to="luggages")
    total_weight = fields.Integer(dump_to="total_weight", dump_only=True)
    total_count = fields.Integer(dump_to="total_count", dump_only=True)


class LuggageItem(serializable.Serializable):

    _schema = LuggageItemSchema()

    def __init__(self):
        super().__init__()
        self.luggage_type = str()
        self.weight_in_lbs = int()


class Luggages(serializable.Serializable):

    _schema = LuggageCollectionSchema()

    def __init__(self):
        super().__init__()
        self._luggage_list = None

    @property
    def luggages(self):
        return self._luggage_list.copy()

    @luggages.setter
    def luggages(self, val):
        self._luggage_list = val.copy()

    @property
    def total_weight(self) -> int:
        return None

    @property
    def total_count(self) -> int:
        return None
