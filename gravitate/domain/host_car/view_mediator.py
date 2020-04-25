import time

from flask_boiler import utils, fields
from flask_boiler.business_property_store import SimpleStore, BPSchema, \
    BusinessPropertyStore
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.struct import Struct
from flask_boiler.view import QueryMediator, ProtocolBase
from google.cloud.firestore import DocumentSnapshot

from gravitate.domain.user import User
from . import RideHost, RideHostReadModel
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
