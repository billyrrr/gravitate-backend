import json

import googlemaps
from flask_boiler.factory import ClsFactory
from flask_boiler import schema, fields, view_model
from flask_boiler.struct import Struct

from gravitate.domain.bookings import RiderBooking
from gravitate.domain.driver_navigation.utils import gmaps
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
        struct["ride_host"] = (RideHost, orbit.ride_host.doc_id)

        struct["rider_bookings"] = {
            booking.doc_id: (RiderBooking, booking.doc_id)
            for booking in orbit.bookings
        }

        return cls.get(struct_d=struct, once=True, **kwargs)

    def _directions(self):
        """
        NOTE: Waypoint may be reordered to the point of reversing from and to
            location of a rider
        :return:
        """
        waypoints = list()
        for _, booking in self.store.rider_bookings.items():
            assert isinstance(booking, RiderBooking)
            waypoints.append("place_id:"+booking.from_location.place_id)
            waypoints.append("place_id:"+booking.to_location.place_id)

        res = gmaps.directions(
            mode='driving',
            origin=self.store.ride_host.from_location.to_coordinate_str(),
            destination=self.store.ride_host.to_location.to_coordinate_str(),
            waypoints=waypoints,
            optimize_waypoints=True,
            departure_time=self.store.ride_host.latest_departure,

        )
        print(json.dumps(res))


    @property
    def timeline(self):
        res = list()
        res.append({
            "description": "Origin",
            "location": self.store.ride_host.from_location.to_dict(),
            "time": self.store.ride_host.earliest_departure
        })
        return res
