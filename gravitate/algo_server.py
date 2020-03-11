import sys
import time
from math import inf

from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV
from google.cloud.firestore import Query
from google.cloud.firestore import DocumentSnapshot

from gravitate.domain import bookings
from gravitate.domain.bookings import RiderBooking
from gravitate.domain.matcher.orbit import Orbit
from gravitate.domain.target import Target
from gravitate.domain import host_car

from gravitate.distance_func import edge_weight


class RiderTargetMediator(ViewMediatorDeltaDAV):

    def __init__(self, *args, target_repo, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_cls = bookings.RiderTarget
        self.target_repo = target_repo

    def _get_query_and_on_snapshot(self):
        query = Query(parent=self.model_cls._get_collection())

        def on_snapshot(snapshots, changes, timestamp):
            for change, snapshot in zip(changes, snapshots):
                if change.type.name == 'ADDED':

                    assert isinstance(snapshot, DocumentSnapshot)
                    obj = snapshot_to_obj(snapshot=snapshot)
                    other = self.target_repo.add(obj)
                    if other is not None:
                        other_target = bookings.RiderTarget.get(
                            doc_ref_str=other)
                        orbit = Orbit.new(status="open")

                        this = RiderBooking.get(doc_ref=obj.r_ref)
                        that = RiderBooking.get(doc_ref=other_target.r_ref)

                        orbit.add_rider(this)
                        orbit.add_rider(that)

        return query, on_snapshot


class HostTargetMediator(ViewMediatorDeltaDAV):

    def __init__(self, *args, target_repo, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_cls = host_car.RideHostTarget
        self.target_repo = target_repo

    def _get_query_and_on_snapshot(self):
        query = Query(parent=self.model_cls._get_collection())

        def on_snapshot(snapshots, changes, timestamp):
            for change, snapshot in zip(changes, snapshots):
                if change.type.name == 'ADDED':

                    assert isinstance(snapshot, DocumentSnapshot)
                    obj = snapshot_to_obj(snapshot=snapshot)
                    self.target_repo.add(obj)

        return query, on_snapshot


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


"""
[BEGIN] ENABLE LOGGING
"""
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
"""
[END] ENABLE LOGGING
"""


if __name__ == '__main__':

    target_repo = TargetRepo()
    rider_target_mediator = RiderTargetMediator(target_repo=target_repo)
    rider_target_mediator.start()

    time.sleep(20)
