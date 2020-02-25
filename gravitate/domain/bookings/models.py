from flask_boiler.schema import Schema
from flask_boiler.fields import Embedded, Integer, Relationship, Boolean, \
    String, Raw
from flask_boiler.domain_model import DomainModel
from flask_boiler.serializable import Serializable


class TargetSchema(Schema):

    earliest_arrival = Integer()
    latest_arrival = Integer()
    earliest_departure = Integer()
    latest_departure = Integer()
    r_ref = Relationship(nested=False)
    from_lat = Raw()
    from_lng = Raw()
    to_lat = Raw()
    to_lng = Raw()


class Target(DomainModel):

    class Meta:
        schema_cls = TargetSchema


class BookingSchema(Schema):

    target = Embedded()

    origin_ref = Relationship()
    destination_ref = Relationship()
    orbit_ref = Relationship()
    user_id = String()
    request_completion = Boolean()


class Booking(DomainModel):

    class Meta:
        schema_cls = BookingSchema
