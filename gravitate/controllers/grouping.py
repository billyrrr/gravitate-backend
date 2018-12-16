from gravitate.controllers import groupingutils
from gravitate.models import Orbit, Event, Location, RideRequest, Target, ToEventTarget
from gravitate.data_access import RideRequestGenericDao, EventDao, LocationGenericDao, OrbitDao, UserDao
from gravitate.controllers import utils
from gravitate import config
from gravitate.controllers import fcmessaging, eventscheduleutils
import warnings
from google.cloud.firestore import Transaction, transactional, DocumentReference

db = config.Context.db


def groupManyRideRequests(rideRequestIds: list):
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


def forceMatchTwoRideRequests(rideRequestIds: list):
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

    groups = list()
    constructGroups(groups, pairedTuples)

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
        [Not Implemented]
        This function 
        1. reads all ride requests associated with an event
        2. puts ride requests into groups
        3. call join method on each group
    :raises:

    :rtype:
    """

    paired, unpaired = pairRideRequests(rideRequests)

    pairedTuples = list()
    convertFirestoreRefTupleListToRideRequestTupleList(paired, pairedTuples)

    groups = list()
    constructGroups(groups, pairedTuples)

    for group in groups:
        group.doWork()


def pairRideRequests(rideRequests: list):
    tupleList = constructTupleList(rideRequests)
    paired = list()
    unpaired = list()
    pair(arr=tupleList, paired=paired, unpaired=unpaired)
    return paired, unpaired


def constructGroups(groups: list, paired: list):
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

    return


def convertFirestoreRefTupleListToRideRequestTupleList(paired: list, results: list):
    for firestoreRef1, firestoreRef2 in paired:
        # TODO change to transaction
        rideRequest1 = RideRequestGenericDao().get(firestoreRef1)
        rideRequest1.setFirestoreRef(firestoreRef1)
        rideRequest2 = RideRequestGenericDao().get(firestoreRef2)
        rideRequest2.setFirestoreRef(firestoreRef2)
        results.append([rideRequest1, rideRequest2])

    return


def constructTupleList(rideRequests: list):
    """ Description

        Note that the rideRequest should only have ToEventTarget as Target

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
    transaction = db.transaction()
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

    transaction = db.transaction()
    groupingutils.removeRideRequestFromOrbit(transaction, rideRequest, orbit)


    transaction = db.transaction()
    UserDao().removeEventScheduleWithTransaction(transaction, userRef=userRef, orbitId=orbitId)

    # TODO update eventSchedule of all participants

    transaction = db.transaction()
    eventSchedule = eventscheduleutils.buildEventSchedule(rideRequest, location=location)
    transaction = db.transaction()
    UserDao().addToEventScheduleWithTransaction(transaction, userRef=userRef, eventRef=eventRef,
                                                eventSchedule=eventSchedule)

    # transaction.commit()

    return True


class Group:

    def __init__(self, rideRequestArray: [], intendedOrbit: Orbit, event: Event, location: Location):
        self.rideRequestArray = rideRequestArray

        # Note that the intended orbit will be in database, and hence possible to be modified by another thread
        self.intendedOrbit = intendedOrbit
        self.event = event
        self.location = location

        self.joined = list()
        self.notJoined = list()

    def doWork(self):
        orbit = self.intendedOrbit

        # Create a transaction so that an exception is thrown when updating an object that is changed since last read from database
        print(self.rideRequestArray)

        for rideRequest in self.rideRequestArray:

            print(rideRequest.toDict())
            transaction: Transaction = db.transaction()

            # Trying to join one rideRequest to the orbit
            isJoined = groupingutils.joinOrbitToRideRequest(transaction, rideRequest, orbit)
            transaction.commit()

            # when failing to join, record and move on to the next
            if isJoined:
                self.joined.append(rideRequest)
            else:
                self.notJoined.append(rideRequest)

        # refresh event schedule for each user
        self.refreshEventSchedules(self.joined, self.intendedOrbit, self.event, self.location)

        return self.notJoined

    @staticmethod
    def refreshEventSchedules(joined, intendedOrbit, event, location):
        rideRequests = joined
        for rideRequest in rideRequests:
            # Note that profile photos may not be populated even after the change is committed
            groupingutils.updateEventSchedule(rideRequest, intendedOrbit, event, location)

    def sendNotifications(self):
        raise NotImplementedError
        # for userId in userIds:
        #     fcmessaging.sendMessageToUser(userId, "You are matched. ")


"""

	Author: Tyler, Zixuan Rao

"""


def pair(arr=None, paired: list = None, unpaired: list = None):
    """
    Description:

        Author: Tyler

        :param arr:  an array of ride requests
            [the first is earliest allowable time, second is latest time, third is firestore reference]
        :param paired:
        :param unpaired:
    """
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
