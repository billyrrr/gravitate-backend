from typing import Type, List, Dict

from gravitate.controllers.grouping.orbit_group import OrbitGroup
from gravitate.controllers.grouping.pairing import pair_ride_requests
from gravitate.models import Orbit, RideRequest
from gravitate.data_access import RideRequestGenericDao, EventDao, LocationGenericDao, OrbitDao
from gravitate import context
import warnings
from google.cloud.firestore import transactional, DocumentReference

db = context.Context.db


def group_many(ride_request_ids: list):
    """
    This function tries to match rideRequests into groups with grouping algorithms.
    Note that the rideRequests may be in different orbits, and rideRequests may not
        be grouped into any orbit.

    :param ride_request_ids:
    :return:
    """
    d = separate_by_event_id(ride_request_ids)

    for event_id in d.keys():
        ride_requests_all = d[event_id]
        pair_list = pair_all(ride_requests_all)
        group_all_pairs_of_event(pair_list)


def separate_by_event_id(ride_request_ids: List[str]) -> Dict[str, List[Type[RideRequest]]]:
    """ Returns a dict with event id as key and ride request object as value
    :param ride_request_ids: a list of ride requests from any number of events
    """
    d = dict()
    for ride_request_id in ride_request_ids:

        ride_request = RideRequestGenericDao().get_by_id(ride_request_id)

        # Do not add to rideRequests queue if the request is complete
        if ride_request.request_completion:
            continue

        event_id = ride_request.event_ref.id
        if event_id not in d.keys():
            d[event_id] = list()
        d[event_id].append(ride_request)
    return d


def pair_all(ride_requests: list) -> list:
    """ Returns a list of list of ride requests.
        Example [ [ride request 1, ride request 3], [ride request 2, ride request 4] ]

    :param ride_requests:
    :return:
    """

    paired, unpaired = pair_ride_requests(ride_requests)
    # Since we are adopting list over tuple
    pairs = [list(pair) for pair in paired]
    return pairs


def group_all_pairs_of_event(pair_list: list) -> list:
    """ Description (Experimental)
        Groups all pairs of ride requests under an event

        This function
        1. reads all ride requests associated with an event
        2. puts ride requests into groups
        3. call join method on each grouping

    :param pair_list: a list of all pairs of ride requests under an event
    :return: a list of ride request ids not joined
    """

    not_joined_all = list()

    for pair in pair_list:
        d = {ref.id: RideRequestGenericDao().get(ref) for ref in pair}
        not_joined = run_orbit_group(d)
        not_joined_all.extend(not_joined)

    return not_joined_all


def group_two(ride_request_ids: list):
    """ Force matches two rideRequests into an orbit.

    :param ride_request_ids: Two rideRequest Ids
    :return:
    """
    ride_requests = [RideRequestGenericDao().get_by_id(rid) for rid in ride_request_ids]

    num_ride_requests = len(ride_requests)
    assert num_ride_requests >= 2

    ride_requests_dict: dict = {
        r.get_firestore_ref().id: r for r in ride_requests
    }
    not_joined_ids = run_orbit_group(ride_requests_dict)

    response_dict = {"notJoined": not_joined_ids}

    return response_dict


def run_orbit_group(ride_requests: dict):
    assert len(ride_requests) != 0
    event_ids: set = {r.event_ref.id for rid, r in ride_requests.items()}
    assert len(event_ids) == 1
    event_ref = EventDao().get_ref(event_ids.pop())

    orbit = Orbit.from_dict({
        "orbitCategory": "airportRide",
        "eventRef": event_ref,
        "userTicketPairs": {
        },
        "chatroomRef": None,
        "costEstimate": 987654321,
        "status": 1
    })
    orbit_ref = OrbitDao().create(orbit)
    orbit.set_firestore_ref(orbit_ref)

    event = EventDao().get(event_ref)
    location_ref: DocumentReference = event.location_ref
    location = LocationGenericDao().get(location_ref)
    ride_request_refs = [r.get_firestore_ref() for rid, r in ride_requests.items()]

    transaction = db.transaction()
    # TODO: implement and call validate_entities_not_changed
    not_joined = _gt(transaction, orbit_ref, ride_request_refs, event_ref, location_ref)
    return not_joined


@transactional
def _gt(transaction, orbit_ref, ride_request_refs, event_ref, location_ref):
    group: OrbitGroup = OrbitGroup(transaction=transaction).setup_with_ref(orbit_ref=orbit_ref,
                                                                           refs_to_add=ride_request_refs,
                                                                           event_ref=event_ref,
                                                                           location_ref=location_ref)
    group.execute()
