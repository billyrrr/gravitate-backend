mport unittest
from data_access.eventSchedule_dao import EventScheduleGenericDao


class EventScheduleDAOTest(unittest.TestCase):

    # def setUp(self):
    #     self.user = User.fromDict(userDict)

    def testCreate(self):
        eventScheduleRef: firestore.DocumentReference = EventScheduleGenericDao().create(self.eventScheduleRef)
        self.eventScheduleRef.setFirestoreRef(eventScheduleRef)
        print("eventScheduleRef = {}".format(eventScheduleRef))