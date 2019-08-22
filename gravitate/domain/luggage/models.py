
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

    _schema_cls = LuggageItemSchema

    def __init__(self):
        super().__init__()
        self.luggage_type = str()
        self.weight_in_lbs = int()


class Luggages(serializable.Serializable):
    """ Keeps track of luggage amount
    """

    _schema_cls = LuggageCollectionSchema

    def __init__(self):
        super().__init__()
        self._luggage_list = []

    @property
    def luggages(self):
        return self._luggage_list.copy()

    @luggages.setter
    def luggages(self, val):
        self._luggage_list = val.copy()

    @property
    def total_weight(self) -> int:
        return self._get_weight()

    @property
    def total_count(self) -> int:
        return self._get_count()

    def add(self, luggage: dict):
        """ Append a piece of luggage to self._luggage_list

        :param luggage:
        :return:
        """
        self._luggage_list.append(luggage)

    def _get_count(self) -> int:
        """ Returns the count for luggages by counting all luggages in self._luggage_list.

        :return:
        """
        return len(self._luggage_list)

    def _get_weight(self) -> int:
        """ Returns the weight for luggages by accumulating all luggages in self._luggage_list.

        :return:
        """
        weight = 0

        for i in self._luggage_list:
            for k, v in i.items():
                if k == "weight_in_lbs":
                    weight += v

        return weight

    def add_from_list(self, l: list):
        """ Add luggages from a list of luggages

        :return:
        """
        for s in l:
            self._luggage_list.append(s)

    def _add_luggages(self, luggages):
        """ Add luggages from another luggages object

        :return:
        """
        luggage_storage = luggages.get_luggage_list()
        for s in luggage_storage:
            self._luggage_list.append(s)

    def get_luggage_list(self):
        """ Return self._luggage_list so that another instance may add luggages in batch
                from this instance.

        :return:
        """
        return self._luggage_list.copy()
