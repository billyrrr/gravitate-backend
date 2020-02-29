import time

from flask_boiler import utils, fields
from flask_boiler.business_property_store import SimpleStore, BPSchema, \
    BusinessPropertyStore
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.struct import Struct
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV
from google.cloud.firestore import DocumentSnapshot

from gravitate.domain.user import User
from . import RiderBooking, BookingStoreBpss
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

        return query, on_snapshot


