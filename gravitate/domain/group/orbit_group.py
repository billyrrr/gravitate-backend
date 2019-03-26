from typing import Type, List

from google.cloud.firestore_v1beta1 import Transaction

from gravitate.data_access import LocationGenericDao, OrbitDao
from gravitate.domain.event.dao import EventDao
from gravitate.domain.event.models import Event
from gravitate.domain.rides import RideRequestGenericDao
from gravitate.models import Orbit, Location
from . import utils


def _refresh_event_schedules_all(transaction: Transaction, in_orbit: dict, not_in_orbit: dict, orbit: Orbit, event,
                                 location):
    """ This function refreshes event schedules of each rideRequests

    :param transaction:
    :param in_orbit:
    :param not_in_orbit:
    :param orbit:
    :param event:
    :param location:
    :return:
    """
    for rid, ride_request in in_orbit.items():
        # (from legacy code:) Note that profile photos may not be populated even after the change is committed
        utils.update_in_orbit_event_schedule(transaction, ride_request, orbit, event, location)

    for rid, ride_request in not_in_orbit.items():
        utils.update_not_in_orbit_event_schedule(transaction, ride_request, event, location)


def _refresh_ride_requests_all(transaction: Transaction, in_orbit: dict, not_in_orbit: dict, orbit: Orbit, event,
                               location):
    """ This function refreshes each rideRequests

    :param transaction:
    :param in_orbit:
    :param not_in_orbit:
    :param orbit:
    :param event:
    :param location:
    :return:
    """
    for rid, ride_request in in_orbit.items():
        RideRequestGenericDao.set_with_transaction(transaction, ride_request, ride_request.get_firestore_ref())

    for rid, ride_request in not_in_orbit.items():
        RideRequestGenericDao.set_with_transaction(transaction, ride_request, ride_request.get_firestore_ref())


def id_set_from_dict(d: dict) -> set:
    return {k for k, v in d.items()}


class OrbitGroup:
    """
    This class handles operations of grouping ride requests into orbits.
    Compared to Group, this new class has better atomicity.

    (Experimental)

    TODO: test

    """

    transaction: Transaction

    # To be set in setup
    orbit: Orbit = None
    ride_requests_to_add: dict = None
    ride_requests_to_drop: dict = None
    ride_requests_existing: dict = None  # key: ride request document id; value: ride request object
    location: Type[Location] = None
    event: Event = None

    def __init__(self, transaction):
        # Start a transaction
        self.transaction = transaction

    def setup_with_ref(self, orbit_ref=None, refs_to_add: list = None, refs_to_drop: list = None,
                       event_ref=None, location_ref=None):
        return self.setup(orbit_ref.id, ids_to_add={ref.id for ref in refs_to_add},
                          ids_to_drop={ref.id for ref in refs_to_drop},
                          event_id=event_ref.id,
                          location_id=location_ref.id)

    def setup(self, intended_orbit_id=None, ids_to_add: set = None, ids_to_drop: set = None, event_id=None,
              location_id=None):
        self.orbit = OrbitGroup._get_orbit(transaction=self.transaction, orbit_id=intended_orbit_id)
        self.ride_requests_existing = \
            OrbitGroup._get_existing_ride_requests(transaction=self.transaction, orbit=self.orbit)
        self.ride_requests_to_add = OrbitGroup._get_ride_requests(transaction=self.transaction, ids=ids_to_add)
        self.ride_requests_to_drop = OrbitGroup._get_ride_requests(transaction=self.transaction, ids=ids_to_drop)
        self.location = OrbitGroup._get_location(transaction=self.transaction, location_id=location_id)
        self.event = OrbitGroup._get_event(transaction=self.transaction, event_id=event_id)

        self._validate_setup()  # Validate fields
        return self

    @staticmethod
    def _get_event(transaction: Transaction = None, event_id: str = None) -> Type[Event]:
        event_ref = EventDao().get_ref(event_id)
        return EventDao().get_with_transaction(transaction, event_ref)

    @staticmethod
    def _get_location(transaction: Transaction = None, location_id: str = None) -> Type[Location]:
        location_ref = LocationGenericDao().get_ref_by_id(location_id)
        return LocationGenericDao.get_with_transaction(transaction, location_ref)

    @staticmethod
    def _get_orbit(transaction: Transaction = None, orbit_id: str = None) -> Orbit:
        orbit_ref = OrbitDao().ref_from_id(orbit_id)
        return OrbitDao.get_with_transaction(transaction, orbit_ref)

    @staticmethod
    def _get_existing_ride_requests(transaction: Transaction = None, orbit: Orbit = None) -> dict:
        refs = [ticket["rideRequestRef"] for user_id, ticket in orbit.user_ticket_pairs.items()]
        ride_requests = {ref.id: RideRequestGenericDao.get_with_transaction(transaction, ref) for ref in refs}
        return ride_requests

    def _validate_setup(self):

        def validate_to_add_ids(existing, to_add):
            """ Check that we are not adding ride request to one that already exists.

            :param existing:
            :param to_add:
            :return:
            """
            existing_ids: set = id_set_from_dict(existing)
            to_add_ids: set = id_set_from_dict(to_add)
            assert not existing_ids & to_add_ids

        def validate_to_drop_ids(existing, to_drop):
            """ Check that the ids to drop are all in existing_ids
            :param existing:
            :param to_drop:
            :return:
            """
            existing_ids: set = id_set_from_dict(existing)
            to_drop_ids: set = id_set_from_dict(to_drop)
            assert to_drop_ids.issubset(existing_ids)

        def validate_no_drop_and_add(to_add, to_drop):
            """ Check that no id is to be dropped and added
            :param to_add:
            :param to_drop:
            :return:
            """
            to_add_ids: set = id_set_from_dict(to_add)
            to_drop_ids: set = id_set_from_dict(to_drop)
            assert not to_drop_ids & to_add_ids

        validate_to_add_ids(self.ride_requests_existing, self.ride_requests_to_add)
        # TODO: validate
        self._assert_elo_not_none()

    def _assert_elo_not_none(self):
        assert self.event is not None
        assert self.location is not None
        assert self.orbit is not None

    def validate_entities_not_changed(self):
        # TODO: implement
        raise NotImplementedError

    def execute(self) -> set:
        """
                This method puts rideRequests into orbit and update participants eventSchedule in atomic operations.
                :return: a list of rideRequests that are not joined
                """
        transaction = self.transaction
        orbit = self.orbit

        # Create a transaction so that an exception is thrown when updating an object that is
        #   changed since last read from database

        existing_ids = {rid for rid, r in self.ride_requests_existing.items()}

        joined_ids, not_joined_ids = OrbitGroup._add(to_add=self.ride_requests_to_add, orbit=orbit)
        dropped_ids, not_dropped_ids = OrbitGroup._drop(to_drop=self.ride_requests_to_drop, orbit=orbit)

        # Update database copy of rideRequests that was just joined
        # TODO: Implement update_all method to refresh all ride requests dropped, added, and etc.
        #   (no need for now since ride request is independent from orbit)
        # TODO: test that all ride requests are covered

        # Update database copy of orbit
        OrbitDao.set_with_transaction(
            transaction, orbit, orbit.get_firestore_ref())

        # refresh event schedule for each user

        in_orbit: dict = OrbitGroup._get_in_orbit(existing_ids=id_set_from_dict(self.ride_requests_existing),
                                                  just_joined_ids=joined_ids,
                                                  just_exited_ids=dropped_ids,
                                                  existing_r=self.ride_requests_existing,
                                                  to_add_r=self.ride_requests_to_add,
                                                  to_drop_r=self.ride_requests_to_drop)

        not_in_orbit: dict = OrbitGroup._get_not_in_orbit(not_joined_ids=not_joined_ids, dropped_ids=dropped_ids,
                                                          existing_r=self.ride_requests_existing,
                                                          to_drop_r=self.ride_requests_to_drop)

        _refresh_ride_requests_all(transaction=transaction, in_orbit=in_orbit, not_in_orbit=not_in_orbit,
                                   orbit=orbit, event=self.event, location=self.location)

        _refresh_event_schedules_all(transaction=transaction, in_orbit=in_orbit, not_in_orbit=not_in_orbit,
                                     orbit=orbit, event=self.event, location=self.location)

        print(
            "About to commit: just joined ids {}; not joined ids {}; just dropped ids: {}; not_dropped_ids: {}; all ids in orbit after operation: {}"
            .format(joined_ids, not_joined_ids, dropped_ids, not_dropped_ids, in_orbit.keys()))

        return not_joined_ids

    @staticmethod
    def _add(to_add, orbit) -> (List[str], List[str]):
        """ Add ride request to orbit

        :param to_add:
        :return: (joined, not_j)
        """
        joined_ids = set()
        not_joined_ids = set()

        for rid, r in to_add.items():

            print(r.to_dict())

            # Join one rideRequest to the orbit
            is_joined = utils.add_orbit_to_ride_request(r, orbit)

            # when failing to join, record and move on to the next
            if is_joined:
                joined_ids.add(rid)
            else:
                not_joined_ids.add(rid)
        return joined_ids, not_joined_ids

    @staticmethod
    def _drop(to_drop, orbit) -> (List[str], List[str]):
        dropped_ids = set()
        not_dropped_ids = set()

        for rid, r in to_drop.items():
            # TODO: implement
            print(r.to_dict())

            # Drop one rideRequest from the orbit
            # utils.remove_ride_request_from_orbit()
            # Join one rideRequest to the orbit
            is_dropped = utils.drop_orbit_from_ride_request(r, orbit)

            # when failing to join, record and move on to the next
            if is_dropped:
                dropped_ids.add(rid)
            else:
                not_dropped_ids.add(rid)
        return dropped_ids, not_dropped_ids

    @staticmethod
    def _get_not_in_orbit(not_joined_ids: set, dropped_ids: set, existing_r: dict, to_drop_r) -> dict:
        a = {rid: r for rid, r in existing_r.items() if rid in not_joined_ids}
        b = {rid: r for rid, r in to_drop_r.items() if rid in dropped_ids}
        d = dict()
        d.update(a)
        d.update(b)
        return d

    @staticmethod
    def _get_in_orbit(existing_ids: set, just_joined_ids: set, just_exited_ids: set, existing_r: dict,
                      to_add_r: dict, to_drop_r: dict) -> dict:
        """ Returns ride requests as a dict to refresh eventSchedule.

        :param existing_ids:
        :param just_joined_ids:
        :param existing_r:
        :param to_add_r:
        :return:
        """
        in_orbit_ids = (existing_ids | just_joined_ids) - just_exited_ids

        def get_ride_requests_all() -> dict:
            """
            Returns a union of ride requests
            :return:
            """
            d: dict = dict(existing_r)
            d.update(to_add_r)
            d.update(to_drop_r)
            return d

        ride_requests_all: dict = get_ride_requests_all()

        return {rid: r for rid, r in ride_requests_all.items() if rid in in_orbit_ids}

    #
    # @staticmethod
    # def _get_ride_requests_to_add(transaction: Transaction=None, ids: set=None) -> dict:
    #     refs = [RideRequestGenericDao().ref_from_id(rid) for rid in ids]
    #     ride_requests = {ref.id: RideRequestGenericDao.get_with_transaction(transaction, ref) for ref in refs}
    #     return ride_requests

    @staticmethod
    def _get_ride_requests(transaction: Transaction = None, ids: set = None) -> dict:
        if ids is None:
            return dict()
        else:
            refs = [RideRequestGenericDao().ref_from_id(rid) for rid in ids]
            ride_requests = {ref.id: RideRequestGenericDao.get_with_transaction(transaction, ref) for ref in refs}
            return ride_requests
