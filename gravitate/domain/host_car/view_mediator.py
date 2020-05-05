import time

from flask_boiler import utils, fields
from flask_boiler.business_property_store import SimpleStore, BPSchema, \
    BusinessPropertyStore
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.struct import Struct
from flask_boiler.view import QueryMediator, ProtocolBase
from flask_boiler.view.query_delta import ViewMediatorDeltaDAV
from google.cloud.firestore import DocumentSnapshot

from gravitate.domain.user import User
from . import RideHost, RideHostReadModel, RideHostForm
from google.cloud.firestore import Query


class UserHostingMediator(QueryMediator):
    """
    Forwards a host ride to a user subcollection
    """

    model_cls = RideHost

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot, mediator):
            obj = RideHostReadModel.new(snapshot=snapshot)
            mediator.notify(obj=obj)

    def notify(self, obj):
        obj.save()


class UserHostingEditMediator(ViewMediatorDeltaDAV):
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

            hosting_id = path.id
            user_id = path.parent.parent.id

            d = snapshot.to_dict()

            obj = RideHostForm.from_dict(doc_id=hosting_id,
                                             d=dict(**d, user_id=user_id))

            mediator.notify(obj=obj)
            snapshot.reference.delete()
