import sys
import time
from math import inf

from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view import QueryMediator
from flask_boiler.view.query_delta import ProtocolBase
from google.cloud.firestore import Query
from google.cloud.firestore import DocumentSnapshot

from gravitate.domain import bookings
from gravitate.domain.bookings import RiderBooking
from gravitate.domain.matcher.orbit import Orbit
from gravitate.domain.target import Target
from gravitate.domain import host_car

from gravitate.distance_func import edge_weight


class RiderTargetMediator(QueryMediator):

    def __init__(self, *args, target_repo, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_cls = bookings.RiderTarget
        self.target_repo = target_repo

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator):

            assert isinstance(snapshot, DocumentSnapshot)
            obj = snapshot_to_obj(snapshot=snapshot)
            other = mediator.target_repo.add(obj)
            if other is not None:
                other_target = bookings.RiderTarget.get(
                    doc_ref_str=other)
                orbit_id = Orbit.create_one()
                Orbit.add_rider(
                    orbit_id=orbit_id, booking_id=obj.r_ref.id)
                Orbit.add_rider(
                    orbit_id=orbit_id, booking_id=other_target.r_ref.id
                )


class HostTargetMediator(QueryMediator):

    def __init__(self, *args, target_repo, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_cls = host_car.RideHostTarget
        self.target_repo = target_repo

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator):
            assert isinstance(snapshot, DocumentSnapshot)
            obj = snapshot_to_obj(snapshot=snapshot)
            mediator.target_repo.add(obj)


class TargetRepo:
    """
    Perform range and proximity search using Brute Force
    TODO: change to K-D Tree
    """

    def __init__(self):
        self.d = dict()

    def add(self, target: Target):
        target_node = target.to_graph_node()
        res = list()
        for key, val in self.d.items():
            dist = edge_weight(target_node, val)
            if dist < inf:
                item = (dist, key)
                res.append(item)
        self.d[target.doc_ref_str] = target_node
        res.sort()
        if len(res) == 0:
            return None
        else:
            return res[0][1]


if __name__ == '__main__':

    target_repo = TargetRepo()
    rider_target_mediator = RiderTargetMediator(
        target_repo=target_repo,
        query=Target.get_query()
    )
    rider_target_mediator.start()

    time.sleep(20)
