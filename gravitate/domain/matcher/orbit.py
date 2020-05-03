import time
from typing import Type

from flask_boiler import attrs
from flask_boiler import schema, fields, domain_model
from flask_boiler.struct import Struct
from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view import QueryMediator, ProtocolBase
from flask_boiler.view_model import ViewModel
from flask_boiler.business_property_store import BPSchema
from google.cloud.firestore import DocumentSnapshot, DocumentReference, Query
from google.cloud.firestore_v1 import transactional

from gravitate import CTX
from gravitate.domain.bookings import RiderBooking
from gravitate.domain.host_car import RideHost
from gravitate.domain.location.models import Sublocation
from gravitate.domain.user_new import User
from gravitate.domain.user_new.view import CoriderView, RideHostUserView


class OrbitSchema(schema.Schema):
    bookings = fields.Relationship(nested=True, many=True)
    ride_host = fields.Relationship(nested=True, many=False, allow_none=True)
    status = fields.Raw()
    user_ticket_pairs = fields.Raw(missing=dict)


class OrbitBase(domain_model.DomainModel):
    class Meta:
        collection_name = "Orbit"


class Orbit(OrbitBase):
    class Meta:
        schema_cls = OrbitSchema

    @classmethod
    def create_one(cls):
        obj = cls.new(status="open")
        obj.save()
        return obj.doc_id

    @classmethod
    def add_rider(cls, *args, **kwargs):
        transaction = CTX.db.transaction()

        @transactional
        def _add_rider_transactional(transaction, orbit_id, booking_id,
                                     **kwargs):
            orbit = cls.get(doc_id=orbit_id, transaction=transaction)
            rider_booking = RiderBooking.get(
                doc_id=booking_id,
                transaction=transaction
            )
            orbit._add_rider(rider_booking,
                             **kwargs)

            orbit.save(transaction=transaction)
            rider_booking.save(transaction=transaction)

        return _add_rider_transactional(
            transaction=transaction, *args, **kwargs
        )

    def _add_rider(self, rider_booking: RiderBooking,
                   pickup_sublocation_id=None,
                   dropoff_sublocation_id=None,
                   ):
        if rider_booking.status != "created":
            raise ValueError
        rider_booking.orbit_ref = self.doc_ref
        rider_booking.status = "matched"
        self.bookings.append(rider_booking)
        self.user_ticket_pairs[rider_booking.user_id] = {
            "bookingId": rider_booking.doc_id,
            "userWillDrive": False,
            "hasCheckedIn": False,
            "state": "added",
            "pickupSublocationId": pickup_sublocation_id,
            "dropoffSublocationId": dropoff_sublocation_id
        }

        # rider_booking.save()
        # self.save()

    @classmethod
    def add_host(cls, *args, **kwargs):
        transaction = CTX.db.transaction()

        @transactional
        def _add_host_transactional(transaction, orbit_id, hosting_id):
            orbit = cls.get(doc_id=orbit_id, transaction=transaction)
            ride_host = RideHost.get(
                doc_id=hosting_id,
                transaction=transaction
            )
            orbit._add_host(ride_host)

            orbit.save(transaction=transaction)
            ride_host.save(transaction=transaction)

        return _add_host_transactional(
            transaction=transaction, *args, **kwargs
        )

    @classmethod
    def match(cls, orbit_id=None, hosting_id=None, rider_records=None):
        transaction = CTX.db.transaction()

        @transactional
        def _match_transactional(transaction, orbit_id=None, hosting_id=None,
                                 rider_records=None):
            if orbit_id is None:
                orbit: Orbit = cls.new(status="open", transaction=transaction)
            else:
                orbit = cls.get(doc_id=orbit_id, transaction=transaction)
            ride_host = RideHost.get(
                doc_id=hosting_id,
                transaction=transaction
            )
            orbit._add_host(ride_host)

            for booking_id, pickup_sublocation_id, dropoff_sublocation_id in rider_records:
                rider_booking = RiderBooking.get(
                    doc_id=booking_id,
                    transaction=transaction
                )
                orbit._add_rider(rider_booking=rider_booking,
                                 pickup_sublocation_id=pickup_sublocation_id,
                                 dropoff_sublocation_id=dropoff_sublocation_id)
                # rider_booking.save(transaction=transaction)

            orbit.save(transaction=transaction)
            # ride_host.save(transaction=transaction)

        return _match_transactional(
            transaction=transaction, orbit_id=orbit_id, hosting_id=hosting_id,
            rider_records=rider_records
        )

    def _add_host(self, ride_host: RideHost):
        if ride_host.status != "created":
            raise ValueError
        ride_host.orbit_ref = self.doc_ref
        ride_host.status = "matched"
        self.ride_host = ride_host
        self.user_ticket_pairs[ride_host.user_id] = {
            "hostId": ride_host.doc_id,
            "userWillDrive": True,
            "hasCheckedIn": False,
            "state": "added"
        }


class OrbitViewBpss(BPSchema):
    bookings = fields.StructuralRef(dm_cls=RiderBooking, many=True)
    ride_host = fields.StructuralRef(dm_cls=RideHost, many=False)
    orbit = fields.StructuralRef(dm_cls=Orbit, many=False)


class OrbitView(ViewModel):

    coriders = attrs.bproperty()
    host_user = attrs.bproperty()
    status = attrs.bproperty()
    timeline = attrs.bproperty()

    @status.getter
    def status(self):
        return self.store.orbit.status

    @coriders.getter
    def coriders(self):
        res = dict()
        for user_id, ticket in self.store.orbit.user_ticket_pairs.items():
            if ticket["userWillDrive"]:
                continue
            user = User.get(doc_id=user_id)
            pickup_location = Sublocation.get(doc_id=ticket["pickupSublocationId"])
            dropoff_location = Sublocation.get(doc_id=ticket["dropoffSublocationId"])
            booking_id = ticket["bookingId"]
            booking = self.store.bookings[booking_id]
            view = CoriderView.new(
                user=user,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                booking=booking
            )
            res[user_id] = view.to_view_dict()
        return res

    @host_user.getter
    def host_user(self):
        for user_id, ticket in self.store.orbit.user_ticket_pairs.items():
            if not ticket["userWillDrive"]:
                continue
            user = User.get(doc_id=user_id)
            return RideHostUserView.new(user=user).to_view_dict()

    @timeline.getter
    def timeline(self):
        from gravitate.domain.matcher.timeline import Timeline
        return Timeline.new(orbit=self.store.orbit).timeline

    @classmethod
    def new(cls, snapshot=None, **kwargs):

        orbit = snapshot_to_obj(snapshot=snapshot)

        struct = Struct(schema_obj=OrbitViewBpss())

        struct["orbit"] = (Orbit, orbit.doc_id)

        for item in orbit.bookings:
            struct["bookings"][item.doc_id] = (RiderBooking, item.doc_id)

        if orbit.ride_host is not None:
            struct["ride_host"] = (RideHost, orbit.ride_host.doc_id)

        return cls.get(struct_d=struct, **kwargs)

    def save(self, **kwargs):
        for _, booking in self.store.bookings.items():
            doc_ref = CTX.db.document("users/{}/bookings/{}/orbits/{}"
                                      .format(booking.user_id,
                                              booking.doc_id,
                                              self.store.orbit.doc_id)
                                      )
            super().save(doc_ref=doc_ref, save_rel=False, **kwargs)
        if hasattr(self.store, "ride_host"):
            ride_host = self.store.ride_host
            doc_ref = CTX.db.document("users/{}/hostings/{}/orbits/{}"
                                      .format(ride_host.user_id,
                                              ride_host.doc_id,
                                              self.store.orbit.doc_id)
                                      )
            super().save(doc_ref=doc_ref, save_rel=False, **kwargs)


class OrbitViewMediator(QueryMediator):
    """
    Forwards a rider booking to a user subcollection
    """

    model_cls = Orbit

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot, mediator):
            obj = OrbitView.new(
                snapshot=snapshot,
                once=True,
                f_notify=mediator.notify
            )
