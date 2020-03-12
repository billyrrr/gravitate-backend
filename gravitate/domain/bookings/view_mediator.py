import time

from flask_boiler import utils, fields
from flask_boiler.business_property_store import SimpleStore, BPSchema, \
    BusinessPropertyStore
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.struct import Struct
from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV
from google.cloud.firestore import DocumentSnapshot

from gravitate import CTX
from gravitate.domain.user import User
from . import RiderBooking, BookingStoreBpss, RiderTarget
from google.cloud.firestore import Query


class UserBookingMediator(ViewMediatorDeltaDAV):
    """
    Forwards a rider booking to a user subcollection
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_cls = RiderBooking

    def _get_query_and_on_snapshot(self):
        query = Query(parent=self.model_cls._get_collection())

        def on_snapshot(snapshots, changes, timestamp):
            for change, snapshot in zip(changes, snapshots):
                if change.type.name == 'ADDED':

                    # assert issubclass(self.model_cls, RiderBooking)
                    assert isinstance(snapshot, DocumentSnapshot)

                    obj = self.view_model_cls.new(snapshot=snapshot)
                    obj.save()

                elif change.type.name == 'MODIFIED':
                    # Delete users/<user_id>/riderBookings/<doc_id>
                    obj: RiderBooking = snapshot_to_obj(snapshot)
                    if obj.status == "removed":
                        self.view_model_cls.remove_one(obj=obj)

        return query, on_snapshot


class UserBookingEditMediator(ViewMediatorDeltaDAV):
    """
    Forwards a rider booking to a user subcollection
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_query_and_on_snapshot(self):
        query = CTX.db.collection_group("bookings_POST")

        def on_snapshot(snapshots, changes, timestamp):
            for change, snapshot in zip(changes, snapshots):
                if change.type.name == 'ADDED':

                    # assert issubclass(self.model_cls, RiderBooking)
                    assert isinstance(snapshot, DocumentSnapshot)
                    path = snapshot.reference

                    booking_id = path.id
                    user_id = path.parent.parent.id

                    d = snapshot.to_dict()

                    obj = self.view_model_cls.from_dict(doc_id=booking_id,
                                                  d=dict(**d, user_id=user_id)
                    )
                    obj.propagate_change()

        return query, on_snapshot


class BookingTargetMediator(ViewMediatorDeltaDAV):
    """
    Generate booking target from a rider booking newly added or edited.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_cls = RiderBooking

    def _get_query_and_on_snapshot(self):
        query = Query(parent=self.model_cls._get_collection())

        def on_snapshot(snapshots, changes, timestamp):
            """
            Note that server reboot will result in some "Modified" objects
                to be routed as "Added" objects

            :param snapshots:
            :param changes:
            :param timestamp:
            :return:
            """
            for change, snapshot in zip(changes, snapshots):
                if change.type.name == 'ADDED':

                    # assert issubclass(self.model_cls, RiderBooking)
                    assert isinstance(snapshot, DocumentSnapshot)

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
                    target.save()
                elif change.type.name == 'MODIFIED':

                    # assert issubclass(self.model_cls, RiderBooking)
                    assert isinstance(snapshot, DocumentSnapshot)

                    obj: RiderBooking = snapshot_to_obj(snapshot=snapshot)
                    if obj.status in {"matched", }:
                        """
                        Delete targets for matched rider bookings 
                        """
                        booking_ref = obj.doc_ref
                        for target in RiderTarget.where(r_ref=booking_ref):
                            target.delete()

        return query, on_snapshot
