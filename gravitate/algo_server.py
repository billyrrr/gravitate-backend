import sys
import time
from math import inf

from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view import QueryMediator
from flask_boiler.view.query_delta import ProtocolBase
from google.cloud.firestore import Query
from google.cloud.firestore import DocumentSnapshot

from gravitate import CTX
from gravitate.domain import bookings
from gravitate.domain.bookings import RiderBooking, RiderTarget
from gravitate.domain.bookings.view_mediator import BookingTargetMediator
from gravitate.domain.host_car import RideHostTarget
from gravitate.domain.matcher.orbit import Orbit
from gravitate.domain.target import Target
from gravitate.domain import host_car

from gravitate.distance_func import edge_weight


booking_target_mediator = BookingTargetMediator(
    query=RiderBooking.get_query()
)


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
            mediator.target_repo.add(obj)


class HostTargetSearchMediator(QueryMediator):

    def __init__(self, *args, target_repo, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_cls = host_car.RideHost
        self.target_repo = target_repo

    class Protocol(ProtocolBase):

        @staticmethod
        def on_create(snapshot: DocumentSnapshot, mediator):
            assert isinstance(snapshot, DocumentSnapshot)
            obj: host_car.RideHost = snapshot_to_obj(snapshot=snapshot)
            d = dict(
                r_ref=obj.doc_ref,
                from_lat=obj.from_location.coordinates[
                    "latitude"],
                from_lng=obj.from_location.coordinates[
                    "longitude"],
                from_id=obj.from_location.doc_id,
                to_lat=obj.to_location.coordinates["latitude"],
                to_lng=obj.to_location.coordinates["longitude"],
                to_id=obj.to_location.doc_id,
                user_id=obj.user_id
            )

            ts = dict(
                earliest_arrival=obj.earliest_arrival,
                latest_arrival=obj.latest_arrival,
                earliest_departure=obj.earliest_departure,
                latest_departure=obj.latest_departure,
            )

            ts = {k: v for k, v in ts.items() if v is not None}

            target = RideHostTarget.new(
                **d, **ts
            )

            other = mediator.target_repo.search(target)
            if other is not None:
                other_target = bookings.RiderTarget.get(
                    doc_ref_str=other)
                other_rid = mediator.target_repo.d[other]["rid"]
                mediator.target_repo.drop(other_rid)
                Orbit.match(
                    hosting_id=obj.doc_id,
                    rider_records=[(
                                   other_target.r_ref.id,
                                   other_target.from_id,
                                   other_target.to_id)],
                )


class TargetRepo:
    """
    Perform range and proximity search using Brute Force
    TODO: change to K-D Tree
    """

    def __init__(self):
        self.d = dict()

    def drop(self, rid):
        for key in list(self.d):
            if self.d[key]["rid"] == rid:
                del self.d[key]

    def add(self, target: Target):
        target_node = target.to_graph_node()
        self.d[target.doc_ref_str] = target_node
        return None

    def search(self, target: Target):
        target_node = target.to_graph_node()
        res = list()
        for key, val in self.d.items():
            dist = edge_weight(target_node, val)
            if dist < inf:
                item = (dist, key)
                res.append(item)
        if len(res) == 0:
            return None
        else:
            res.sort()
            return res[0][1]


if __name__ == '__main__':

    booking_target_mediator.start()

    target_repo = TargetRepo()
    rider_target_mediator = RiderTargetMediator(
        target_repo=target_repo,
        query=RiderTarget.get_query()
    )
    rider_target_mediator.start()

    time.sleep(10)

    host_target_search_mediator = HostTargetSearchMediator(
        target_repo=target_repo,
        query=host_car.RideHost.get_query()
    )
    host_target_search_mediator.start()

    time.sleep(20)
