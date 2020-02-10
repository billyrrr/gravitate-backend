from flask_boiler.schema import Schema
from flask_boiler.fields import Embedded, Integer, Relationship, Boolean, String
from flask_boiler.domain_model import DomainModel


class TargetSchema(Schema):

    earliest_arrival = Integer()
    latest_arrival = Integer()
    earliest_departure = Integer()
    latest_departure = Integer()


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
