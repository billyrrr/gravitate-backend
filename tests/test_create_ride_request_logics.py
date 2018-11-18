from controllers.process_ride_request import createTarget
from unittest import TestCase

class MockForm:

    def __init__(self):
        self.earliest = "2018-12-20T09:00:00.000"
        self.latest = "2018-12-20T11:00:00.000"
        self.toEvent = True

class testCreateRideRequestLogics(TestCase):

    def testCreateTarget(self):
        mockForm = MockForm()
        targetDict = createTarget(mockForm).toDict()
        print(targetDict)