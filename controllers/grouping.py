from controllers.associate_ride_request_with_orbit import joinOrbitToRideRequest
from models.orbit import Orbit
from data_access.ride_request_dao import RideRequestGenericDao
from controllers.group_user import pair
from models.ride_request import RideRequest, Target, ToEventTarget
import config

db = config.Context.db

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
        print('doing work')
        print(group)
    

def pairRideRequests(rideRequests: list):
    tupleList = constructTupleList(rideRequests)
    paired = list()
    unpaired = list()
    pair(arr=tupleList, paired=paired, unpaired=unpaired)
    return paired, unpaired

def constructGroups(groups: list, paired: list):

    for rideRequest1, rideRequest2 in paired:

        group: Group = Group([rideRequest1, rideRequest2])
        groups.append(group)

    return

def convertFirestoreRefTupleListToRideRequestTupleList(paired: list, results: list):

    for firestoreRef1, firestoreRef2 in paired:
        # TODO change to transaction
        rideRequest1 = RideRequestGenericDao().getRideRequest(firestoreRef1)
        rideRequest2 = RideRequestGenericDao().getRideRequest(firestoreRef2)
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
        toEventTarget: ToEventTarget = rideRequest.target
        earliest = toEventTarget.arriveAtEventTime['earliest']
        latest = toEventTarget.arriveAtEventTime['latest']
        ref = rideRequest.getFirestoreRef()
        tupleToAppend = [earliest, latest, ref]
        arr.append(tupleToAppend)

    return arr

class Group:

    def __init__(self, rideRequestArray:[]):
        self.rideRequestArray = rideRequestArray
        print(rideRequestArray)
        # Note that the intended orbit will be in database, and hence possible to be modified by another thread
        self.intendedOrbit = None # TODO create an orbit (may need a factory pattern) and add to database

    def doWork(self):
        orbit = self.intendedOrbit

        # Record which users failed join the orbit
        notJoined = []

        for rideRequest in self.rideRequestArray:
            try:
                # Trying to join one rideRequest to the orbit
                raise NotImplementedError
                # joinOrbitToRideRequest(client=None, rideRequest.firestoreRef, rideRequest, orbit.firestoreRef, orbit)
            except:
                # TODO when failing to join, move on to next
                notJoined.append(rideRequest)
                raise

        return notJoined
        