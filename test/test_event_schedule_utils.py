import unittest

from google.cloud.firestore import DocumentReference, DocumentSnapshot

from gravitate.domain.event_schedule.utils import getMemberProfilePhotoUrls
from gravitate.models.orbit import Orbit
from gravitate import context
# from firebase_admin import auth

CTX = context.Context
# auth = context.auth

db = CTX.db


class EventScheduleUtilsTest(unittest.TestCase):

    def testPopulateProfileUrls(self):
        orbitRef: DocumentReference = db.collection(u'orbits').document("WQiIEsGlVbU8a8F1la45")
        snapshot: DocumentSnapshot = orbitRef.get()
        if snapshot.exists:
            orbit: Orbit = Orbit.from_dict(snapshot.to_dict())
            print(getMemberProfilePhotoUrls(orbit))
        else:
            print("Not Found")
            return False

    @unittest.skip("not yet implemented. Comment this decorator when test is needed")
    def testCreateCompletedRideRequest(self):
        raise NotImplementedError
        # rideRequest: make a mock ride request that is matched to an orbit
        # orbit: make an orbit that is matched to a pair of users

# class EventScheduleDAOTest(unittest.TestCase):
