from collections import UserDict
import random
from math import inf

from flask_boiler import schema, fields, domain_model
from google.cloud.firestore import DocumentReference


class TargetSchema(schema.Schema):

    earliest_arrival = fields.NumberTimestamp(default=-inf)
    latest_arrival = fields.NumberTimestamp(default=inf)
    earliest_departure = fields.NumberTimestamp(default=-inf)
    latest_departure = fields.NumberTimestamp(default=inf)
    r_ref = fields.Relationship(nested=False)
    from_lat = fields.Raw()
    from_lng = fields.Raw()
    to_lat = fields.Raw()
    to_lng = fields.Raw()
    origin_geohash = fields.Raw(dump_only=True)
    destination_geohash = fields.Raw(dump_only=True)


class TargetNodeSchema(schema.Schema):

    case_conversion = False

    earliest_arrival = fields.Integer()
    latest_arrival = fields.Integer()
    earliest_departure = fields.Integer()
    latest_departure = fields.Integer()
    from_lat = fields.Raw()
    from_lng = fields.Raw()
    to_lat = fields.Raw()
    to_lng = fields.Raw()


def random_integer_id():
    random_id_str = "8" + ''.join(str(random.randint(0, 9)) for n in range(31))
    return random_id_str


class TargetNode(UserDict):

    def __hash__(self):
        return int(self.data["doc_id"])


def get_geohash(value):
    """
    Temporary method for getting geohash
    TODO: replace
    :return:
    """
    val = round(value, 2)
    _offset = 0.01

    return [val+_offset*i for i in range(-3, 4)]


class Target(domain_model.DomainModel):

    random_id = random_integer_id

    class Meta:
        schema_cls = TargetSchema

    @property
    def origin_geohash(self):
        """
        Returns geohash of the origin coordinate
        TODO: change into actual geohash
        :return:
        """
        return self.from_lat

    @property
    def destination_geohash(self):
        """
        Returns geohash of the destination coordinate
        TODO: change into actual geohash
        :return:
        """
        return self.to_lat

    def to_graph_node(self):
        keys = {"from_lat", "from_lng", "to_lat", "to_lng",
                "earliest_arrival", "latest_arrival", "earliest_departure",
                "latest_departure", "doc_id"}
        _d = TargetNodeSchema().dump(self)
        d = {key: _d[key] for key in keys}
        r_ref: DocumentReference = self.r_ref
        d["rid"] = r_ref.id
        return TargetNode(d)
