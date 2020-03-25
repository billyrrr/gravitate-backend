from flask_boiler.factory import ClsFactory
from flask_boiler import schema, fields, view_model
from flask_boiler.struct import Struct

from gravitate.domain.bookings import RiderBooking
from gravitate.domain.host_car import RideHost
from gravitate.domain.matcher.orbit import Orbit


class TimelineSchema(schema.Schema):

    timeline = fields.Raw()


TimelineBase = ClsFactory.create(
    "TimelineBase",
    schema=TimelineSchema,
    base=view_model.ViewModel
)


class TimelineBpss(view_model.BPSchema):
    orbit = fields.StructuralRef(dm_cls=Orbit)
    ride_host = fields.StructuralRef(dm_cls=RideHost)
    rider_bookings = fields.StructuralRef(dm_cls=RiderBooking, many=True)


class Timeline(TimelineBase):

    @classmethod
    def new(cls, *args, orbit: Orbit, **kwargs):

        struct = Struct(schema_obj=TimelineBpss())

        struct["orbit"] = (Orbit, orbit.doc_id)
        struct["ride_host"] = (RideHost, orbit.ride_host.id)

        struct["rider_bookings"] = {
            booking_ref.id: (RiderBooking, booking_ref.id)
            for booking_ref in orbit.bookings
        }

        return cls.get(struct_d=struct, once=True, **kwargs)

    @property
    def timeline(self):
        res = list()
        res.append({
            "description": "Origin",
            "location": self.store.ride_host.from_location.to_dict(),
            "time": self.store.ride_host.earliest_departure
        })
        return res
