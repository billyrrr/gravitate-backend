from controllers.associate_ride_request_with_orbit import joinOrbitToRideRequest
from models.orbit import Orbit
from data_access.ride_request_dao import RideRequestGenericDao
import data_access
from controllers.group_user import pair
from controllers import utils
from models.ride_request import RideRequest, Target, ToEventTarget
import config
from controllers import groupingutils
import warnings

db = config.Context.db



def groupManyRideRequests(rideRequestIds: list):
    rideRequests = list()
    for rideRequestId in rideRequestIds:
        rideRequestRef = db.collection("rideRequests").document(rideRequestId)
        rideRequest = RideRequestGenericDao().get(rideRequestRef)
        rideRequest.setFirestoreRef(rideRequestRef)
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

    # rideRequest Response
    responseDict = {"notJoined": notJoined}
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

        intendedOrbit = Orbit.fromDict({
            "orbitCategory": "airportRide",
            "eventRef": None,
            "userTicketPairs": {
            },
            "chatroomRef": None,
            "costEstimate": 987654321,
            "status": 1
        })
        orbitRef = data_access.OrbitDao().createOrbit(intendedOrbit)
        intendedOrbit.setFirestoreRef(orbitRef)

        group: Group = Group([rideRequest1, rideRequest2], intendedOrbit)
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
            warnings.warn("failed to parse rideRequest: {}".format(rideRequest.toDict()) )
            print("error: {}".format(e))

    return arr

class Group:

    def __init__(self, rideRequestArray:[], intendedOrbit: Orbit):
        self.rideRequestArray = rideRequestArray
        # Note that the intended orbit will be in database, and hence possible to be modified by another thread
        self.intendedOrbit = intendedOrbit
         # TODO create an orbit (may need a factory pattern) and add to database

    def doWork(self):
        orbit = self.intendedOrbit

        # Record which users failed join the orbit
        notJoined = []

        for rideRequest in self.rideRequestArray:
            try:
                groupingutils.placeInOrbit(rideRequest, self.intendedOrbit)
                # Trying to join one rideRequest to the orbit
                # raise NotImplementedError
                joinOrbitToRideRequest( rideRequest.getFirestoreRef(), rideRequest, orbit.getFirestoreRef(), orbit)
                # Save orbit
            except:
                # TODO when failing to join, move on to next
                notJoined.append(rideRequest)
                raise

        return notJoined
        
