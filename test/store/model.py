import json

from gravitate import context
import gravitate.models as models

db = context.Context.db


def getMockKeys(rideRequestId="testriderequestid1", locationId="testairportlocationid1", eventId="testeventid1",
                userId="testuserid1", orbitId="testorbitid1"):
    keys = {
        "rideRequestId": rideRequestId,
        "rideRequestRef": "/rideRequests/" + rideRequestId,
        "rideRequestFirestoreRef": db.collection("rideRequests").document(rideRequestId),
        "locationId": locationId,
        "locationRef": "/locations/" + locationId,
        "locationFirestoreRef": db.collection("locations").document(locationId),
        "eventId": eventId,
        "eventRef": "/events/" + eventId,
        "eventFirestoreRef": db.collection("events").document(eventId),
        "userId": userId,
        "orbitId": orbitId,
        "orbitRef": "/orbits/" + orbitId,
        "orbitFirestoreRef": db.collection("orbits").document(orbitId)
    }

    return keys


mock1 = getMockKeys()


def getMockRideRequest(earliest: int = 1545058800, latest: int = 1545069600, firestoreRef=mock1["rideRequestRef"],
                       userId=mock1["userId"], useDocumentRef=False, returnDict=False, returnSubset=False):
    locationRefStr = mock1["locationRef"]
    locationReference = mock1["locationFirestoreRef"]

    eventRefStr = mock1["eventRef"]
    eventReference = mock1["eventFirestoreRef"]

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
        rideRequest = models.RideRequest.from_dict(rideRequestDict)
        rideRequest.set_firestore_ref(firestoreRef)
        return rideRequest


eventDict = {
    "eventCategory": "airport",
    "participants": [
    ],
    "eventLocation": "LAX",
    "locationRef": mock1["locationRef"],
    "startTimestamp": 1545033600,
    "endTimestamp": 1545119999,
    "pricing": 100,
    "isClosed": False
}


def getEventDict():
    return eventDict


eventScheduleDict = {
    "destName": "LAX",
    "destTime": None,
    "flightTime": "2018-12-17T12:00:00.000",
    "memberProfilePhotoUrls": [],
    "pickupAddress": "Tenaya Hall, San Diego, CA 92161",
    "pending": True,
    "rideRequestRef": mock1["rideRequestRef"],
    "locationRef": mock1["locationRef"],
    "orbitRef": None
}


def getEventScheduleDict():
    return eventScheduleDict


orbitDict = {
    "orbitCategory": "airportRide",
    "eventRef": mock1["eventRef"],
    "userTicketPairs": {
        "testuserid1": {
            "rideRequestRef": None,
            "userWillDrive": False,
            "hasCheckedIn": False,
            "inChat": True,
            "pickupAddress": "testpickupaddress1"
        }
    },
    "chatroomRef": "testchatroomref1",
    "costEstimate": 987654321,
    "status": 1
}


def get_orbit_dict_empty(event_ref):
    return {
        "orbitCategory": "airportRide",
        "eventRef": event_ref,
        "userTicketPairs": {

        },
        "chatroomRef": "testchatroomref1",
        "costEstimate": 987654321,
        "status": 1
}


def getOrbitDict():
    return orbitDict


airportLocationDict = {
    'locationCategory': "airport",
    'coordinates': {
        "latitude": 33.9416,
        "longitude": -118.4085
    },
    'address': "1 World Way, Los Angeles, CA 90045",
    'airportCode': "LAX",
}


def getLocationDict():
    return airportLocationDict


def getLocation():
    locationDict = getLocationDict()
    location = models.Location.from_dict(locationDict)
    location.set_firestore_ref(mock1["locationRef"])
    return location


def get_json_file(json_filename):
    with open('test/jsons_written_by_david_a/{}'.format(json_filename)) as json_file:
        return json.load(json_file)
