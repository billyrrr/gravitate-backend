import unittest
from data_access import EventScheduleGenericDao
from google.cloud.firestore import DocumentReference

class EventScheduleDAOTest(unittest.TestCase):

    # def setUp(self):
    #     self.user = User.fromDict(userDict)

    def testCreate(self):
        eventScheduleRef: DocumentReference = EventScheduleGenericDao().create(self.eventScheduleRef)
        self.eventScheduleRef.setFirestoreRef(eventScheduleRef)
        print("eventScheduleRef = {}".format(eventScheduleRef))