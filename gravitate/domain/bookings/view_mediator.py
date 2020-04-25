import time

from flask_boiler import utils, fields
from flask_boiler.business_property_store import SimpleStore, BPSchema, \
    BusinessPropertyStore
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.struct import Struct
from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV, ProtocolBase
from google.cloud.firestore import DocumentSnapshot

from gravitate import CTX
from gravitate.domain.user import User
from . import RiderBooking, BookingStoreBpss, RiderTarget, RiderBookingView, \
    RiderBookingForm, RiderBookingReadModel
from google.cloud.firestore import Query


class UserBookingMediator(ViewMediatorDeltaDAV):
    """
    Forwards a rider booking to a user subcollection
    """

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot, mediator):
            obj = RiderBookingReadModel.new(snapshot=snapshot)
            mediator.notify(obj=obj)

        @staticmethod
        def on_update(snapshot, mediator):
            obj: RiderBooking = snapshot_to_obj(snapshot)
            if obj.status == "removed":
                RiderBookingReadModel.remove_one(obj=obj)

    model_cls = RiderBooking


class UserBookingEditMediator(ViewMediatorDeltaDAV):
    """
    Forwards a rider booking to a user subcollection
    """

    def notify(self, obj):
        obj.propagate_change()

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot, mediator):
            assert isinstance(snapshot, DocumentSnapshot)
            path = snapshot.reference

            booking_id = path.id
            user_id = path.parent.parent.id

            d = snapshot.to_dict()

            obj = RiderBookingForm.from_dict(doc_id=booking_id,
                                             d=dict(**d, user_id=user_id))

            mediator.notify(obj=obj)
            snapshot.reference.delete()


class BookingTargetMediator(ViewMediatorDeltaDAV):
    """
    Generate booking target from a rider booking newly added or edited.
    """

    model_cls = RiderBooking

    def notify(self, obj):
        obj.save()

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot, mediator):
            obj: RiderBooking = snapshot_to_obj(snapshot=snapshot)
            d = dict(
                r_ref=obj.doc_ref,
                from_lat=obj.from_location.coordinates[
                    "latitude"],
                from_lng=obj.from_location.coordinates[
                    "longitude"],
                to_lat=obj.to_location.coordinates["latitude"],
                to_lng=obj.to_location.coordinates["longitude"]
            )

            ts = dict(
                earliest_arrival=obj.earliest_arrival,
                latest_arrival=obj.latest_arrival,
                earliest_departure=obj.earliest_departure,
                latest_departure=obj.latest_departure,
            )

            ts = {k: v for k, v in ts.items() if v is not None}

            target = RiderTarget.new(
                **d, **ts
            )

            mediator.notify(obj=target)

        @staticmethod
        def on_delete(snapshot, mediator):
            obj: RiderBooking = snapshot_to_obj(snapshot=snapshot)
            if obj.status in {"matched", }:
                """
                Delete targets for matched rider bookings 
                """
                booking_ref = obj.doc_ref
                for target in RiderTarget.where(r_ref=booking_ref):
                    target.delete()

    def _get_query(self):
        query = Query(parent=self.model_cls._get_collection())

        return query
