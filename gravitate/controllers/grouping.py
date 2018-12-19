from gravitate.controllers import groupingutils
from gravitate.models import Orbit, Event, Location, RideRequest, Target, ToEventTarget
from gravitate.data_access import RideRequestGenericDao, EventDao, LocationGenericDao, OrbitDao, UserDao
from gravitate.controllers import utils
from gravitate import config
from gravitate.controllers import fcmessaging, eventscheduleutils
import warnings
from google.cloud.firestore import Transaction, transactional, DocumentReference

db = config.Context.db


def groupMany(rideRequestIds: list):
    """
    This function tries to match rideRequests into groups with grouping algorithms.
    Note that the rideRequests may be in different orbits, and rideRequests may not
        be grouped into any orbit.

    :param rideRequestIds:
    :return:
    """
    rideRequests = list()
    for rideRequestId in rideRequestIds:

        rideRequestRef = db.collection("rideRequests").document(rideRequestId)
        rideRequest = RideRequestGenericDao().get(rideRequestRef)
        rideRequest.setFirestoreRef(rideRequestRef)

        # Do not add to rideRequests queue if the request is complete
        if rideRequest.requestCompletion:
            continue

        rideRequests.append(rideRequest)

    groupRideRequests(rideRequests)


def forceMatchTwo(rideRequestIds: list):
    """
    This function force matches two rideRequests into an orbit.

    :param rideRequestIds: Two rideRequest Ids
    :return:
    """
    rideRequests = list()
    for rideRequestId in rideRequestIds:
        rideRequestRef = db.collection("rideRequests").document(rideRequestId)
        rideRequest = RideRequestGenericDao().get(rideRequestRef)
        rideRequest.setFirestoreRef(rideRequestRef)
        rideRequests.append(rideRequest)

    numRideRequests = len(rideRequests)
    assert numRideRequests >= 2
    if numRideRequests >= 3:
        warnings.warn(
            "Orbit is only tested for matching 2 rideRequests. " +
            "You are forcing to match {} users in one orbit. ".format(numRideRequests) +
            "Only rideRequests {} and {} are expected be matched. "
            .format(rideRequests[0].toDict(), rideRequests[1].toDict()))

    pairedTuples = [(rideRequests[0], rideRequests[1])]

    groups = constructGroups(pairedTuples)

    group = groups[0]
    notJoined = group.doWork()
    notJoinedIds = list()

    for rideRequestNotJoined in notJoined:
        notJoinedIds.append(rideRequestNotJoined.getFirestoreRef())

    # rideRequest Response
    responseDict = {"notJoined": notJoinedIds}
    return responseDict


def groupRideRequests(rideRequests: list):
    """ Description
        This function
        1. reads all ride requests associated with an event
        2. puts ride requests into groups
        3. call join method on each group
    :raises:

    :rtype:
    """

    paired, unpaired = pairRideRequests(rideRequests)

    pairedTuples = convertFirestoreRefTupleListToRideRequestTupleList(paired)

    groups = constructGroups(pairedTuples)

    for group in groups:
        group.doWork()


def pairRideRequests(rideRequests: list):
    """
    This function serves as an adaptor for grouping algorithms.
    :param rideRequests:
    :return:
    """
    tupleList = constructTupleList(rideRequests)
    paired, unpaired = pair(arr=tupleList)
    return paired, unpaired


def constructGroups(paired: list) -> list:
    """ Description
        This function converts a list of rideRequestId pairs to a list of groups.

    :param paired: list of rideRequestId pairs
        Example: [ (testriderequest1, testriderequest3), (testriderequest2, testriderequest4) ]
    :return: list of groups
    """
    groups = list()

    for rideRequest1, rideRequest2 in paired:
        assert rideRequest1.eventRef.id == rideRequest2.eventRef.id
        eventRef = rideRequest1.eventRef

        intendedOrbit = Orbit.fromDict({
            "orbitCategory": "airportRide",
            "eventRef": eventRef,
            "userTicketPairs": {
            },
            "chatroomRef": None,
            "costEstimate": 987654321,
            "status": 1
        })
        orbitRef = OrbitDao().create(intendedOrbit)
        intendedOrbit.setFirestoreRef(orbitRef)
        event = EventDao().get(eventRef)
        locationRef: DocumentReference = event.locationRef
        location = LocationGenericDao().get(locationRef)

        rideRequests = list()
        rideRequests.append(rideRequest1)
        rideRequests.append(rideRequest2)

        group: Group = Group(rideRequests, intendedOrbit, event, location)
        groups.append(group)

    return groups


def convertFirestoreRefTupleListToRideRequestTupleList(paired: list):
    """ Description
    This function is an adaptor to convert tuples of rideRequestRef as returned by grouping
        algorithm to tuples of rideRequest objects that the system may do operations on.

    :param paired:
    :param results:
    :return:
    """
    results = list()

    for firestoreRef1, firestoreRef2 in paired:
        # TODO change to transaction
        rideRequest1 = RideRequestGenericDao().get(firestoreRef1)
        rideRequest1.setFirestoreRef(firestoreRef1)
        rideRequest2 = RideRequestGenericDao().get(firestoreRef2)
        rideRequest2.setFirestoreRef(firestoreRef2)
        results.append([rideRequest1, rideRequest2])

    return results


def constructTupleList(rideRequests: list):
    """ Description
        This function constructs tuple list consisting only variables relevant to the
            grouping algorithm.
        Note that this function only supports rideRequests with ToEventTarget as Target.

        :type rideRequests:list:
        :param rideRequests:list:
    
        :raises:
    
        :rtype:
    """
    arr = list()

    for rideRequest in rideRequests:
        try:
            toEventTarget: ToEventTarget = rideRequest.target
            earliest = toEventTarget.arriveAtEventTime['earliest']
            latest = toEventTarget.arriveAtEventTime['latest']
            ref = rideRequest.getFirestoreRef()
            tupleToAppend = [earliest, latest, ref]
            arr.append(tupleToAppend)
        except Exception as e:
            warnings.warn("failed to parse rideRequest: {}".format(rideRequest.toDict()))
            print("error: {}".format(e))

    return arr


def remove(rideRequestRef: DocumentReference) -> bool:
    """
    This method removes/unmatches rideRequest from the orbit it associates with.

    :param rideRequestRef:
    :return: True if successful
    """
    transaction = db.transaction()
    _remove(transaction, rideRequestRef)
    return True


@transactional
def _remove(transaction, rideRequestRef: DocumentReference):
    """
    This method removes/unmatches rideRequest from the orbit it associates with.
    (Transactional business logic for use case unmatch from orbit)

    :param transaction:
    :param rideRequestRef:
    :return:
    """
    rideRequest = RideRequestGenericDao().getWithTransaction(transaction, rideRequestRef)
    rideRequest.setFirestoreRef(rideRequestRef)

    userId = rideRequest.userId
    userRef = UserDao().getRef(userId)
    # user = UserDao().getUserWithTransaction(transaction, userRef)

    orbitRef = rideRequest.orbitRef

    assert orbitRef != None

    orbitId = orbitRef.id
    orbit = OrbitDao().getWithTransaction(transaction, orbitRef)
    orbit.setFirestoreRef(orbitRef)

    eventRef = orbit.eventRef

    locationRef: DocumentReference = rideRequest.airportLocation
    location = LocationGenericDao().getWithTransaction(transaction, locationRef)

    groupingutils.removeRideRequestFromOrbit(transaction, rideRequest, orbit)

    # Delete current user eventSchedule that is associated with an orbit
    UserDao().removeEventScheduleWithTransaction(transaction, userRef=userRef, orbitId=orbitId)

    # TODO update eventSchedule of all participants

    # Build new eventSchedule that is not associated with any orbit and marked as pending
    eventSchedule = eventscheduleutils.buildEventSchedule(rideRequest, location=location)
    UserDao().addToEventScheduleWithTransaction(transaction, userRef=userRef, eventRef=eventRef,
                                                eventSchedule=eventSchedule)


class Group:
    """
    This class stores rideRequests that will be grouped into the same orbit, and provides operations.

    """

    def __init__(self, rideRequestArray: [], intendedOrbit: Orbit, event: Event, location: Location):
        """

        :param rideRequestArray: a list of rideRequests to be grouped into the orbit
        :param intendedOrbit: the orbit object to group rideRequests into
        :param event: the event object since we are matching "rideRequests that go to the same event"
        :param location: the location object for the event (example: location representing LAX)
        """
        self.rideRequestArray = rideRequestArray

        # Note that the intended orbit will be in database, and hence possible to be modified by another thread
        self.intendedOrbit = intendedOrbit
        self.event = event
        self.location = location

        self.joined = list()
        self.notJoined = list()

    def doWork(self):
        """
        This method puts rideRequests into orbit and update participants eventSchedule in atomic operations.
        :return: a list of rideRequests that are not joined
        """
        orbit = self.intendedOrbit

        # Create a transaction so that an exception is thrown when updating an object that is
        #   changed since last read from database
        transaction: Transaction = db.transaction()

        for rideRequest in self.rideRequestArray:

            print(rideRequest.toDict())

            # Trying to join one rideRequest to the orbit
            isJoined = groupingutils.joinOrbitToRideRequest(transaction, rideRequest, orbit)

            # TODO: modify logics to make sure that rideRequests in "joined" are actually joined
            # when failing to join, record and move on to the next
            if isJoined:
                self.joined.append(rideRequest)
            else:
                self.notJoined.append(rideRequest)

        # refresh event schedule for each user
        self.refreshEventSchedules(transaction, self.joined, self.intendedOrbit, self.event, self.location)

        transaction.commit()

        return self.notJoined

    @staticmethod
    def refreshEventSchedules(transaction: Transaction, joined, intendedOrbit, event, location):
        """
        This function refreshes event schedules of each rideRequests in joined

        :param transaction:
        :param joined: the rideRequests joined by the algorithm
        :param intendedOrbit:
        :param event:
        :param location:
        :return:
        """
        rideRequests = joined
        for rideRequest in rideRequests:
            # Note that profile photos may not be populated even after the change is committed
            groupingutils.updateEventSchedule(transaction, rideRequest, intendedOrbit, event, location)

    def sendNotifications(self, userIds: list) -> bool:
        """ Description
        This function sends notifications to each user in userIds.

        :param userIds:
        :return:
        """
        raise NotImplementedError
        # for userId in userIds:
        #     fcmessaging.sendMessageToUser(userId, "You are matched. ")


"""

	Author: Tyler, Zixuan Rao

"""


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
