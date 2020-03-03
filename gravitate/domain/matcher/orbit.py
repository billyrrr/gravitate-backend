import time

from flask_boiler import schema, fields, domain_model
from flask_boiler.struct import Struct
from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV
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

        return cls.get(struct_d=struct, once=False, **kwargs)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_cls = Orbit

    def _get_query_and_on_snapshot(self):
        query = Query(parent=self.model_cls._get_collection())

        def on_snapshot(snapshots, changes, timestamp):
            for change, snapshot in zip(changes, snapshots):
                if change.type.name == 'ADDED':

                    obj = self.view_model_cls.new(
                        snapshot=snapshot,
                        f_notify=self.notify
                    )
                    # time.sleep(5)
                    # print(obj.store)

        return query, on_snapshot
