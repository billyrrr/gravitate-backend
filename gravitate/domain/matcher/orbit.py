import time

from flask_boiler import schema, fields, domain_model
from flask_boiler.struct import Struct
from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV, ProtocolBase
from flask_boiler.view_model import ViewModel
from flask_boiler.business_property_store import BPSchema
from google.cloud.firestore import DocumentSnapshot, DocumentReference, Query

from gravitate import CTX
from gravitate.domain.bookings import RiderBooking
from gravitate.domain.host_car import RideHost


class OrbitSchema(schema.Schema):

    bookings = fields.Relationship(nested=False, many=True)
    ride_host = fields.Relationship(nested=False, many=False)

    status = fields.Raw()


class OrbitBase(domain_model.DomainModel):

    class Meta:
        collection_name = "Orbit"


class Orbit(OrbitBase):

    class Meta:
        schema_cls = OrbitSchema

    def add_rider(self, rider_booking: RiderBooking):
        rider_booking.orbit_ref = self.doc_ref
        rider_booking.status = "matched"
        self.bookings.append(rider_booking.doc_ref)

        rider_booking.save()
        self.save()

    def add_host(self, ride_host: RideHost):
        ride_host.orbit_ref = self.doc_ref
        self.ride_host = ride_host.doc_ref

        ride_host.save()
        self.save()


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


class OrbitViewMediator(ViewMediatorDeltaDAV):
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
