import sys
import time

from flask_boiler.utils import snapshot_to_obj
from flask_boiler.view_mediator_dav import ViewMediatorDeltaDAV
from google.cloud.firestore import Query
from google.cloud.firestore import DocumentSnapshot

from gravitate.domain import bookings
from gravitate.domain.target import Target
from gravitate.domain import host_car

from networkx import Graph


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
                    self.target_repo.add(obj)

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

    def __init__(self, graph):
        self.d = dict()
        self.graph = graph

    def add(self, target: Target):
        from gravitate.distance_func import edge_weight
        self.d[target.doc_ref_str] = target
        new_node = target.to_graph_node()
        graph.add_node(new_node)
        for node in graph.nodes:
            if node == new_node:
                continue
            weight = edge_weight(node, new_node)
            graph.add_weighted_edges_from(
                ebunch_to_add={(node, new_node, weight)})


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

    graph = Graph()

    target_repo = TargetRepo(graph)
    rider_target_mediator = RiderTargetMediator(target_repo=target_repo)
    rider_target_mediator.start()

    host_target_mediator = HostTargetMediator(target_repo=target_repo)
    host_target_mediator.start()

    time.sleep(5)
