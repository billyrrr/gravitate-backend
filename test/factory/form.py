class MockFl3Form(object):

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


class MockFl3FormBuilder(MockFl3Form):

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


class AMockFormBuilder(MockFl3FormBuilder):

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
        mockForm = MockFl3FormBuilder()
        return mockForm

    def create(self, hasEarliestLatest=False, isE5L2=True, returnDict=True):

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

class EventRideRequestFormDictFactory:

    def create(self):
        return {
             'userId': 'testuserid1',
             'eventId': "KxkUnYurkYL1hZGHdxUY",
             'pickupAddress': 'Tenaya Hall, San Diego, CA 92161',
             'driverStatus': False,
             'toEvent': True
        }
