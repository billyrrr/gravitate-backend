import time
from typing import Type

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
        def _add_rider_transactional(transaction, orbit_id, booking_id, **kwargs):
            orbit = cls.get(doc_id=orbit_id, transaction=transaction)
            rider_booking = RiderBooking.get(
                doc_id=booking_id,
                transaction=transaction
            )
            orbit._add_rider(rider_booking,
                             **kwargs)

            orbit.save(transaction=transaction)
            # rider_booking.save(transaction=transaction)

        return _add_rider_transactional(
            transaction=transaction, *args, **kwargs
        )

    def _add_rider(self, rider_booking: RiderBooking,
                   pickup_sublocation_id=None,
                   dropoff_sublocation_id=None,
                   ):
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
            # ride_host.save(transaction=transaction)

        return _add_host_transactional(
            transaction=transaction, *args, **kwargs
        )

    def _add_host(self, ride_host: RideHost):
        ride_host.orbit_ref = self.doc_ref
        self.ride_host = ride_host
        self.user_ticket_pairs[ride_host.user_id] = {
            "hostId": ride_host.doc_id,
            "userWillDrive": True,
            "hasCheckedIn": False,
            "state": "added"
        }


class OrbitViewSchema(schema.Schema):

    users = fields.List(dump_only=True)
    bookings = fields.Relationship(nested=True, many=True, dump_only=True)
    ride_host = fields.Raw(dump_only=True)

    status = fields.Raw(dump_only=True)


class OrbitViewBpss(BPSchema):
    bookings = fields.StructuralRef(dm_cls=RiderBooking, many=True)
    ride_host = fields.StructuralRef(dm_cls=RideHost, many=False)
    orbit = fields.StructuralRef(dm_cls=Orbit, many=False)


class OrbitView(ViewModel):

    class Meta:
        schema_cls = OrbitViewSchema

    @property
    def status(self):
        return self.store.orbit.status

    @property
    def bookings(self):
        return self.store.bookings

    @property
    def ride_host(self):
        return self.store.ride_host.to_dict()

    @property
    def users(self):
        # TODO: implement
        return []

    @classmethod
    def new(cls, snapshot=None, **kwargs):

        orbit = snapshot_to_obj(snapshot=snapshot)

        struct = Struct(schema_obj=OrbitViewBpss())

        struct["orbit"] = (Orbit, orbit.doc_id)

        for item in orbit.bookings:
            assert isinstance(item, DocumentReference)
            struct["bookings"][item.id] = (RiderBooking, item.id)

        if orbit.ride_host is not None:
            struct["ride_host"] = (RideHost, orbit.ride_host.id)

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
                once=True
            )
            mediator.notify(obj=obj)
