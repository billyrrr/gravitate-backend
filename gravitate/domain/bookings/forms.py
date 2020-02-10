from flask_boiler.schema import Schema
from flask_boiler.fields import Nested, Integer, Relationship, Boolean, \
    String, Raw
from flask_boiler.view_model import ViewModel

from gravitate.common import local_time_from_timestamp, \
    timestamp_from_local_time
from gravitate.domain.location import Location
from .models import Booking


class BookingFormSchema(Schema):
    origin_id = String()
    destination_id = String()
    constraints = Raw(load_only=True)
    user_id = String()
    booking = Relationship(nested=True)


class BookingForm(ViewModel):

    class Meta:
        schema_cls = BookingFormSchema

    @classmethod
    def new(cls, *args, **kwargs):
        return super().new(*args, booking=Booking.new(), **kwargs)

    @property
    def origin_id(self):
        return self.booking.origin_ref.id

    @origin_id.setter
    def origin_id(self, value):
        self.booking.origin_ref = Location.ref_from_id(doc_id=value)

    @property
    def destination_id(self):
        return self.booking.destination_ref.id

    @destination_id.setter
    def destination_id(self, value):
        self.booking.destination_ref = Location.ref_from_id(doc_id=value)

    def _get_time(self, attr_name):
        timestamp = getattr(self.booking.target, attr_name)
        return local_time_from_timestamp(timestamp)

    def _set_time(self, attr_name, s):
        local_time = timestamp_from_local_time(s)
        setattr(self.booking.target, attr_name, local_time)

    @property
    def constraints(self):
        raise AttributeError

    @constraints.setter
    def constraints(self, value):
        for key, val in value.items():
            setattr(self, key, val)

    @property
    def earliest_departure(self):
        return self._get_time("earliest_departure")

    @earliest_departure.setter
    def earliest_departure(self, value):
        self._set_time("earliest_departure", value)

    @property
    def latest_departure(self):
        return self._get_time("latest_departure")

    @latest_departure.setter
    def latest_departure(self, value):
        self._set_time("latest_departure", value)

    @property
    def earliest_arrival(self):
        return self._get_time("earliest_arrival")

    @earliest_arrival.setter
    def earliest_arrival(self, value):
        self._set_time("earliest_arrival", value)

    @property
    def latest_arrival(self):
        return self._get_time("latest_arrival")

    @latest_arrival.setter
    def latest_arrival(self, value):
        self._set_time("latest_arrival", value)

