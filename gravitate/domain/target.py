from collections import UserDict
import random

from flask_boiler import schema, fields, domain_model


class TargetSchema(schema.Schema):

    earliest_arrival = fields.Integer()
    latest_arrival = fields.Integer()
    earliest_departure = fields.Integer()
    latest_departure = fields.Integer()
    r_ref = fields.Relationship(nested=False)
    from_lat = fields.Raw()
    from_lng = fields.Raw()
    to_lat = fields.Raw()
    to_lng = fields.Raw()


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


class Target(domain_model.DomainModel):

    random_id = random_integer_id

    class Meta:
        schema_cls = TargetSchema

    def to_graph_node(self):
        keys = {"from_lat", "from_lng", "to_lat", "to_lng",
                "earliest_arrival", "latest_arrival", "earliest_departure",
                "latest_departure", "doc_id"}
        _d = TargetNodeSchema().dump(self)
        return TargetNode({key: _d[key] for key in keys})
