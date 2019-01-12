from gravitate.controllers.grouping import utils
from gravitate.models import Orbit, Event, Location, ToEventTarget
from gravitate.data_access import RideRequestGenericDao, EventDao, LocationGenericDao, OrbitDao, UserDao
from gravitate import context
from gravitate.controllers import eventscheduleutils
import warnings
from google.cloud.firestore import Transaction, transactional, DocumentReference

db = context.Context.db


def group_many(ride_request_ids: list):
    """
    This function tries to match rideRequests into groups with grouping algorithms.
    Note that the rideRequests may be in different orbits, and rideRequests may not
        be grouped into any orbit.

    :param ride_request_ids:
    :return:
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

    for event_id in d.keys():
        ride_requests = d[event_id]
        group_ride_requests(ride_requests)


def group_two(ride_request_ids: list):
    """
    This function force matches two rideRequests into an orbit.

    :param ride_request_ids: Two rideRequest Ids
    :return:
    """
    ride_requests = [RideRequestGenericDao().get_by_id(rid) for rid in ride_request_ids]

    num_ride_requests = len(ride_requests)
    assert num_ride_requests >= 2
    if num_ride_requests >= 3:
        warnings.warn(
            "Orbit is only tested for matching 2 rideRequests. " +
            "You are forcing to match {} users in one orbit. ".format(num_ride_requests) +
            "Only rideRequests {} and {} are expected be matched. "
            .format(ride_requests[0].to_dict(), ride_requests[1].to_dict()))

    paired_tuples = [(ride_requests[0], ride_requests[1])]

    groups = construct_groups(paired_tuples)

    group = groups[0]
    not_joined = group.do_work()
    not_joined_ids = list()

    for rideRequestNotJoined in not_joined:
        not_joined_ids.append(rideRequestNotJoined.get_firestore_ref())

    # rideRequest Response
    response_dict = {"notJoined": not_joined_ids}
    return response_dict


def group_ride_requests(ride_requests: list):
    """ Description
        This function
        1. reads all ride requests associated with an event
        2. puts ride requests into groups
        3. call join method on each grouping
    :raises:

    :rtype:
    """

    paired, unpaired = pair_ride_requests(ride_requests)

    paired_tuples = convert_firestore_ref_tuple_list_to_ride_request_tuple_list(paired)

    groups = construct_groups(paired_tuples)

    for group in groups:
        group.do_work()


def pair_ride_requests(ride_requests: list):
    """
    This function serves as an adaptor for grouping algorithms.
    :param ride_requests:
    :return:
    """
    tuple_list = construct_tuple_list(ride_requests)
    paired, unpaired = pair(arr=tuple_list)
    return paired, unpaired


def construct_groups(paired: list) -> list:
    """ Description
        This function converts a list of rideRequestId pairs to a list of groups.

    :param paired: list of rideRequestId pairs
        Example: [ (testriderequest1, testriderequest3), (testriderequest2, testriderequest4) ]
    :return: list of groups
    """
    groups = list()

    for rideRequest1, rideRequest2 in paired:
        assert rideRequest1.event_ref.id == rideRequest2.event_ref.id
        event_ref = rideRequest1.event_ref

        intended_orbit = Orbit.from_dict({
            "orbitCategory": "airportRide",
            "eventRef": event_ref,
            "userTicketPairs": {
            },
            "chatroomRef": None,
            "costEstimate": 987654321,
            "status": 1
        })
        orbit_ref = OrbitDao().create(intended_orbit)
        intended_orbit.set_firestore_ref(orbit_ref)
        event = EventDao().get(event_ref)
        location_ref: DocumentReference = event.location_ref
        location = LocationGenericDao().get(location_ref)

        ride_requests = list()
        ride_requests.append(rideRequest1)
        ride_requests.append(rideRequest2)

        group: Group = Group(ride_requests, intended_orbit, event, location)
        groups.append(group)

    return groups


def convert_firestore_ref_tuple_list_to_ride_request_tuple_list(paired: list):
    """ Description
    This function is an adaptor to convert tuples of rideRequestRef as returned by grouping
        algorithm to tuples of rideRequest objects that the system may do operations on.
    TODO: place in package and rename

    :param paired:
    :param results:
    :return:
    """
    results = list()

    for firestoreRef1, firestoreRef2 in paired:
        # TODO change to transaction
        ride_request1 = RideRequestGenericDao().get(firestoreRef1)
        ride_request1.set_firestore_ref(firestoreRef1)
        ride_request2 = RideRequestGenericDao().get(firestoreRef2)
        ride_request2.set_firestore_ref(firestoreRef2)
        results.append([ride_request1, ride_request2])

    return results


def construct_tuple_list(ride_requests: list):
    """ Description
        This function constructs tuple list consisting only variables relevant to the
            grouping algorithm.
        Note that this function only supports rideRequests with ToEventTarget as Target.

        :type ride_requests:list:
        :param ride_requests:list:
    
        :raises:
    
        :rtype:
    """
    arr = list()

    for ride_request in ride_requests:
        try:
            to_event_target: ToEventTarget = ride_request.target
            earliest = to_event_target.arrive_at_event_time['earliest']
            latest = to_event_target.arrive_at_event_time['latest']
            ref = ride_request.get_firestore_ref()
            tuple_to_append = [earliest, latest, ref]
            arr.append(tuple_to_append)
        except Exception as e:
            warnings.warn("failed to parse rideRequest: {}".format(ride_request.to_dict()))
            print("error: {}".format(e))

    return arr


def remove(ride_request_ref: DocumentReference) -> bool:
    """
    This method removes/unmatches rideRequest from the orbit it associates with.

    :param ride_request_ref:
    :return: True if successful
    """
    transaction = db.transaction()
    _remove(transaction, ride_request_ref)
    return True


@transactional
def _remove(transaction, ride_request_ref: DocumentReference):
    """
    This method removes/unmatches rideRequest from the orbit it associates with.
    (Transactional business logic for use case unmatch from orbit)

    :param transaction:
    :param ride_request_ref:
    :return:
    """
    ride_request = RideRequestGenericDao().get_with_transaction(transaction, ride_request_ref)
    ride_request.set_firestore_ref(ride_request_ref)

    user_id = ride_request.user_id
    user_ref = UserDao().get_ref(user_id)
    # user = UserDao().get_user_with_transaction(transaction, userRef)

    orbit_ref = ride_request.orbit_ref

    assert orbit_ref is not None

    orbit_id = orbit_ref.id
    orbit = OrbitDao().get_with_transaction(transaction, orbit_ref)
    orbit.set_firestore_ref(orbit_ref)

    event_ref = orbit.event_ref

    location_ref: DocumentReference = ride_request.airport_location
    location = LocationGenericDao().get_with_transaction(transaction, location_ref)

    utils.remove_ride_request_from_orbit(transaction, ride_request, orbit)

    # Delete current user eventSchedule that is associated with an orbit
    UserDao().remove_event_schedule_with_transaction(transaction, userRef=user_ref, orbitId=orbit_id)

    # TODO update eventSchedule of all participants

    # Build new eventSchedule that is not associated with any orbit and marked as pending
    event_schedule = eventscheduleutils.buildEventSchedule(ride_request, location=location)
    UserDao().add_to_event_schedule_with_transaction(transaction, user_ref=user_ref, event_ref=event_ref,
                                                     event_schedule=event_schedule)


class Group:
    """
    This class stores rideRequests that will be grouped into the same orbit, and provides operations.

    """

    def __init__(self, ride_request_array: [], intended_orbit: Orbit, event: Event, location: Location):
        """

        :param ride_request_array: a list of rideRequests to be grouped into the orbit
        :param intended_orbit: the orbit object to grouping rideRequests into
        :param event: the event object since we are matching "rideRequests that go to the same event"
        :param location: the location object for the event (example: location representing LAX)
        """
        self.ride_request_array = ride_request_array

        # Note that the intended orbit will be in database, and hence possible to be modified by another thread
        self.intended_orbit = intended_orbit
        self.event = event
        self.location = location

        self.joined = list()
        self.not_joined = list()

    def do_work(self):
        """
        This method puts rideRequests into orbit and update participants eventSchedule in atomic operations.
        :return: a list of rideRequests that are not joined
        """
        orbit = self.intended_orbit

        # Create a transaction so that an exception is thrown when updating an object that is
        #   changed since last read from database
        transaction: Transaction = db.transaction()

        for ride_request in self.ride_request_array:

            print(ride_request.to_dict())

            # Trying to join one rideRequest to the orbit
            is_joined = utils.join_orbit_to_ride_request(ride_request, orbit)

            # TODO: modify logics to make sure that rideRequests in "joined" are actually joined
            # when failing to join, record and move on to the next
            if is_joined:
                self.joined.append(ride_request)
            else:
                self.not_joined.append(ride_request)

        for ride_request in self.joined:
            # Update database copy of rideRequest and orbit
            RideRequestGenericDao.set_with_transaction(
                transaction, ride_request, ride_request.get_firestore_ref())

        OrbitDao.set_with_transaction(
            transaction, orbit, orbit.get_firestore_ref())

        # refresh event schedule for each user
        self.refresh_event_schedules(transaction, self.joined, self.intended_orbit, self.event, self.location)

        transaction.commit()

        return self.not_joined

    def do_work_experimental(self):
        """
        Experimental feature for N+1 joining
        This method puts rideRequests into orbit and update participants eventSchedule in atomic operations.
        :return: a list of rideRequests that are not joined
        """
        orbit = self.intended_orbit

        # Create a transaction so that an exception is thrown when updating an object that is
        #   changed since last read from database
        transaction: Transaction = db.transaction()

        for rideRequest in self.ride_request_array:

            print(rideRequest.to_dict())

            # Trying to join one rideRequest to the orbit
            is_joined = utils.join_orbit_to_ride_request(rideRequest, orbit)

            # TODO: modify logics to make sure that rideRequests in "joined" are actually joined
            # when failing to join, record and move on to the next
            if is_joined:
                self.joined.append(rideRequest)
            else:
                self.not_joined.append(rideRequest)

        for rideRequest in self.joined:
            # Update database copy of rideRequest and orbit
            RideRequestGenericDao.set_with_transaction(
                transaction, rideRequest, rideRequest.get_firestore_ref())

        OrbitDao.set_with_transaction(
            transaction, orbit, orbit.get_firestore_ref())

        # refresh event schedule for each user
        # TODO: refresh eventSchedules on all rideRequests in an orbit rather than those just joined
        self.refresh_event_schedules(transaction, self.joined, self.intended_orbit, self.event, self.location)

        transaction.commit()

        ids_in_orbit = list()

        def ids_from_pairs():
            for user_id, ticket in orbit.user_ticket_pairs.items():
                ids_in_orbit.append(ticket["rideRequestRef"].id)

        ids_from_pairs()

        ids_just_joined = list()

        def ids_from_joined():
            for ride_request in self.joined:
                ids_just_joined.append(ride_request.get_firestore_ref().id)

        ids_from_joined()

        ids_to_refresh = list(set(ids_in_orbit) - set(ids_just_joined))
        for id in ids_to_refresh:
            # TODO: add code for refreshing ride_requests
            raise NotImplementedError

        return self.not_joined

    @staticmethod
    def refresh_event_schedules(transaction: Transaction, joined, intended_orbit, event, location):
        """
        This function refreshes event schedules of each rideRequests in joined

        :param transaction:
        :param joined: the rideRequests joined by the algorithm
        :param intended_orbit:
        :param event:
        :param location:
        :return:
        """
        ride_requests = joined
        for ride_request in ride_requests:
            # Note that profile photos may not be populated even after the change is committed
            utils.update_event_schedule(transaction, ride_request, intended_orbit, event, location)

    def send_notifications(self, userIds: list) -> bool:
        """ Description
        This function sends notifications to each user in userIds.

        :param userIds:
        :return:
        """
        raise NotImplementedError
        # for userId in userIds:
        #     fcmessaging.sendMessageToUser(userId, "You are matched. ")


def pair(arr=None) -> (list, list):
    """
    Description

        Author: Tyler

        :param arr:  an array of ride requests
            [the first is earliest allowable time, second is latest time, third is firestore reference]
        :param paired:
        :param unpaired:
    """

    paired = list()
    unpaired = list()

    sortedArr = sorted(arr, key=lambda x: x[0])

    i = 0
    while i < len(sortedArr):

        if i == len(sortedArr) - 1:
            unpaired.insert(len(unpaired), [sortedArr[i][2]])
            i += 1
        else:
            if (sortedArr[i][1] >= sortedArr[i + 1][0]):

                paired.insert(len(paired), [sortedArr[i][2], sortedArr[i + 1][2]])
                i += 1
            else:

                unpaired.insert(len(unpaired), [sortedArr[i][2]])
            i += 1
    return paired, unpaired
