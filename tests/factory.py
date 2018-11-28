class MockForm:

    def __init__(self):
        
        
        self.earliest = "2018-12-17T09:00:00.000"
        self.latest = "2018-12-17T11:00:00.000"
        self.toEvent = True
        
        self.driverStatus = False
        self.pickupAddress = "Tenaya Hall, San Diego, CA 92161"

        self.airportLocation = "LAX TBIT Terminal"
        self.flightLocalTime = "2018-12-17T12:00:00.000"
        self.flightNumber = "DL89"
    
    def toDict(self):
        return vars(self)

class FormDictFactory:
    def create(self):
        return MockForm().toDict()

    def createForm(self):
        return MockForm()