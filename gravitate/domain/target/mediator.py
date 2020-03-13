from flask_boiler.query.cmp import v
from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV, ProtocolBase
from google.cloud.firestore import DocumentSnapshot, Query

from gravitate.domain.bookings import RiderTarget


class TargetMatchMediator(ViewMediatorDeltaDAV):
    """
    Match newly added Target to existing ones
    """

    model_cls = RiderTarget

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot, mediator):
            obj: RiderTarget = snapshot_to_obj(snapshot=snapshot)
            mediator.notify(obj=obj)

    def notify(self, obj):
        obj.save()
