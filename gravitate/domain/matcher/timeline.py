import json

import googlemaps
from flask_boiler.factory import ClsFactory
from flask_boiler import schema, fields, view_model
from flask_boiler.struct import Struct

from gravitate.domain.bookings import RiderBooking
from gravitate.domain.driver_navigation.utils import gmaps
from gravitate.domain.host_car import RideHost
from gravitate.domain.location.models import Sublocation
from gravitate.domain.matcher.orbit import Orbit

from gravitate.domain.user_new import User


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
        for user_id, ticket in self.store.orbit.user_ticket_pairs.items():
            if ticket["userWillDrive"]:
                continue
            booking = self.store.rider_bookings[ticket["bookingId"]]
            assert isinstance(booking, RiderBooking)
            pickup_sublocation = Sublocation.get(doc_id=ticket["pickupSublocationId"])
            waypoints.append(pickup_sublocation.to_coordinate_str())
            dropoff_sublocation = Sublocation.get(doc_id=ticket["dropoffSublocationId"])
            waypoints.append(dropoff_sublocation.to_coordinate_str())

        res = gmaps.directions(
            mode='driving',
            origin=self.store.ride_host.from_location.to_coordinate_str(),
            destination=self.store.ride_host.to_location.to_coordinate_str(),
            waypoints=waypoints,
            optimize_waypoints=False,
            departure_time=self.store.ride_host.latest_departure,
        )
        # print(json.dumps(res))

    @property
    def timeline(self):
        res = list()
        res.append({
            "description": f"{User.get(doc_id=self.store.ride_host.user_id).name} will depart from {self.store.ride_host.from_location.address}",
            "latitude": self.store.ride_host.from_location.latitude,
            "longitude": self.store.ride_host.from_location.longitude,
            "time": self.store.ride_host.earliest_departure
        })

        for user_id, ticket in self.store.orbit.user_ticket_pairs.items():
            if ticket["userWillDrive"]:
                continue
            booking = self.store.rider_bookings[ticket["bookingId"]]
            assert isinstance(booking, RiderBooking)
            pickup_sublocation = Sublocation.get(doc_id=ticket["pickupSublocationId"])
            res.append({
                "description":  f"{User.get(doc_id=booking.user_id).name} will be picked up from {pickup_sublocation.road_name}",
                "latitude": booking.from_location.latitude,
                "longitude": booking.from_location.longitude,
                "time": booking.earliest_departure
            })
            dropoff_sublocation = Sublocation.get(doc_id=ticket["dropoffSublocationId"])
            res.append({
                "description": f"{User.get(doc_id=booking.user_id).name} will be dropped off at {dropoff_sublocation.road_name}",
                "latitude": booking.to_location.latitude,
                "longitude": booking.to_location.longitude,
                "time": booking.earliest_departure
            })

        res.append({
            "description":  f"{User.get(doc_id=self.store.ride_host.user_id).name} will arrive at {self.store.ride_host.to_location.address}",
            "latitude": self.store.ride_host.to_location.latitude,
            "longitude": self.store.ride_host.to_location.longitude,
            "time": self.store.ride_host.earliest_departure
        })

        return res
