import models
import config

db = config.Context.db

class MockForm(object):

    def __init__(self):
        
        
        self.earliest = None
        self.latest = None
        self.toEvent = None
        
        self.driverStatus = None
        self.pickupAddress = None

        self.airportCode = None
        self.flightLocalTime = None
        self.flightNumber = None
    
    def toDict(self):
        return vars(self)

class MockFormBuilder(MockForm):

    def __init__(self):
        self.buildAirportInfo()
        self.buildUserTravelOptions()
        self.buildFlight()

    def buildAirportInfo(self):
        raise NotImplementedError()

    def buildUserTravelOptions(self):
        raise NotImplementedError()

    def buildFlight(self):
        raise NotImplementedError()

class AMockFormBuilder(MockFormBuilder):

    def buildAirportInfo(self):
        self.airportCode = "LAX"

    def buildUserTravelOptions(self):
        self.toEvent = True
        self.driverStatus = False
        self.pickupAddress = "Tenaya Hall, San Diego, CA 92161"

    def buildFlight(self):
        self.flightLocalTime = "2018-12-17T12:00:00.000"
        self.flightNumber = "DL89"

class BMockFormBuilder(AMockFormBuilder):

    def __init__(self):
        super().__init__()
        self.buildEarliestLatest()

    def buildEarliestLatest(self):
        self.earliest = "2018-12-17T09:00:00.000"
        self.latest = "2018-12-17T11:00:00.000"
    
class CMockFormBuilder(AMockFormBuilder):

    def __init__(self):
        super().__init__()
        self.buildEarliestLatest()

    def buildEarliestLatest(self):
        self.earliest = "2018-12-17T07:00:00.000"
        self.latest = "2018-12-17T10:00:00.000"

class FormDictFactory:
    def createDict(self):
        return BMockFormBuilder().toDict()

    def createForm(self):
        return BMockFormBuilder()

    def createFormNoEarliestLatest(self):
        mockForm = MockFormBuilder()
        return mockForm

    def create(self, hasEarliestLatest = False, isE5L2 = True, returnDict = True):

        mockForm = None

        if (hasEarliestLatest):
            if isE5L2:
                mockForm = CMockFormBuilder()
            else:
                mockForm = BMockFormBuilder()
        else:
            mockForm = AMockFormBuilder()
        
        if returnDict:
            return mockForm.toDict()
        else:
            return mockForm


def getMockRideRequest(earliest: int = 1545058800, latest: int = 1545069600,  firestoreRef='/rideRequests/testRef1', userId='SQytDq13q00e0N3H4agR', useDocumentRef = False, returnDict = False, returnSubset = False):
    
    locationRefStr = "/locations/testairportlocationid1"
    locationReference = db.collection("locations").document("testairportlocationid1")

    eventRefStr = "/events/testeventid1"
    eventReference = db.collection("events").document("testeventid")

    rideRequestDict = {

            'rideCategory': 'airportRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'airportRide',
                         'toEvent': True,
                         'arriveAtEventTime':
                         {'earliest': earliest, 'latest': latest}},
            
            'userId': userId,
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),
            'flightLocalTime': "2018-12-17T12:00:00.000",
            'flightNumber': "DL89",
            
            "requestCompletion": False

        }

    if not returnSubset:
        rideRequestDict["airportLocation"] = locationReference if useDocumentRef else locationRefStr
        rideRequestDict["eventRef"] = eventReference if useDocumentRef else eventRefStr

    if returnDict:
        return rideRequestDict
    else:
        rideRequest = models.ride_request.RideRequest.fromDict(rideRequestDict)
        rideRequest.setFirestoreRef(firestoreRef)
        return rideRequest