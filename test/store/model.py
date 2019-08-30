import json

# import gravitate.models as models
from gravitate import context
from gravitate.domain.rides import RideRequest
from gravitate.domain.location import Location

db = context.Context.db

def getMockKeys(rideRequestId="testriderequestid1", locationId="testairportlocationid1", eventId="testeventid1",
                userId="testuserid1", orbitId="testorbitid1", originId="testlocation1", destinationId="testlaxlocation1"):
    keys = {
        "rideRequestId": rideRequestId,
        "rideRequestRef": "/rideRequests/" + rideRequestId,
        "rideRequestFirestoreRef": db.collection("rideRequests").document(rideRequestId),
        "locationId": locationId,
        "locationRef": "/locations/" + locationId,
        "locationFirestoreRef": db.collection("locations").document(locationId),
        "originId": originId,
        "originRef": "/locations/" + originId,
        "originFirestoreRef": db.collection("locations").document(originId),
        "destinationId": destinationId,
        "destinationRef": "/locations/" + destinationId,
        "destinationFirestoreRef": db.collection("locations").document(destinationId),
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


def getMockRideRequestDeprecated(earliest: int = 1545058800, latest: int = 1545069600, firestoreRef=mock1["rideRequestRef"],
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
        rideRequest = RideRequest.from_dict(rideRequestDict)
        rideRequest.set_firestore_ref(firestoreRef)
        return rideRequest

def getMockRide(earliest: int = 1545058800, latest: int = 1545069600, firestoreRef=mock1["rideRequestRef"],
                       userId=mock1["userId"], useDocumentRef=False, returnDict=False, returnSubset=False, driverStatus=False):
    locationRefStr = mock1["locationRef"]
    locationReference = mock1["locationFirestoreRef"]

    originRefStr = mock1["originRef"]
    originReference = mock1["originFirestoreRef"]

    destinationRefStr = mock1["destinationRef"]
    destinationReference = mock1["destinationFirestoreRef"]

    eventRefStr = mock1["eventRef"]
    eventReference = mock1["eventFirestoreRef"]

    rideRequestDict = {

        'rideCategory': 'airportRide',

        'driverStatus': driverStatus,
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
        rideRequestDict['originRef'] =  originReference if useDocumentRef else originRefStr
        rideRequestDict['destinationRef'] = destinationReference if useDocumentRef else destinationRefStr

    if returnDict:
        return rideRequestDict
    else:
        rideRequest = RideRequest.from_dict(rideRequestDict)
        rideRequest.set_firestore_ref(firestoreRef)
        return rideRequest


getMockRideRequest = getMockRide

"""
Monday, December 17, 2018 12:00:00 AM GMT-08:00 to
Monday, December 17, 2018 11:59:59 PM GMT-08:00
"""

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

#
# def getEventDict(event_category="airport", use_firestore_ref=False):
#
#     d = None
#
#     if event_category == "airport":
#         d = {
#             "eventCategory": "airport",
#             "participants": [
#             ],
#             "eventLocation": "LAX",
#
#             "startTimestamp": 1545033600,
#             "endTimestamp": 1545119999,
#             "pricing": 100,
#             "isClosed": False
#         }
#     elif event_category == "social":
#         d = {
#             "eventCategory": "social",
#             "participants": [
#             ],
#             "eventLocation": "Las Vegas Convention Center",
#
#             "startTimestamp": 1545033600,
#             "endTimestamp": 1545119999,
#             "pricing": 100,
#             "isClosed": False
#         }
#     else:
#         raise ValueError("event_category not supported: {}".format(event_category))
#
#     d["locationRef"] = mock1["locationFirestoreRef"] if use_firestore_ref else mock1["locationRef"]
#
#     return d


def getEventDict(event_category="airport", use_firestore_ref=False,
                 to_earliest=1545066000, to_latest=1545073200,
                 from_earliest=1545066000, from_latest=1545073200):
    d = None
    if event_category == "airport":
        d = {
            "eventCategory": "airport",
            "participants": [
            ],
            "targets": [
                {
                    'eventCategory': 'airportRide',
                    'toEvent': True,
                    'arriveAtEventTime': {'earliest': to_earliest, 'latest': to_latest}
                },
                {
                    'eventCategory': 'airportRide',
                    'toEvent': False,
                    'leaveEventTime': {'earliest': from_earliest, 'latest': from_latest}
                }
            ],
            "airportCode": "LAX",
            "localDateString": "2018-12-17",  # YYYY-MM-DD
            "pricing": 100,
            "isClosed": False,
            "parkingInfo": {
                "parkingAvailable": False,
                "parkingPrice": 0,
                "parkingLocation": "none"
            },
            "description": "what the event is",
            "name": "name of the event",
            # "locationRef": "/locations/testlocationid1"
        }
    elif event_category == "social":
        d = {
            "eventCategory": "social",
            "isClosed": False,
            "targets": [
                {'eventCategory': 'social', 'toEvent': True,
                 'arriveAtEventTime': {'earliest': 1555077600, 'latest': 1555088400}},
                {'eventCategory': 'social', 'toEvent': False,
                 'leaveEventTime': {'earliest': 1555318740, 'latest': 1555329540}},
            ],
            "localDateString": "2019-04-12",
            "pricing": 123456789,
            "parkingInfo": None,
            "description": "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com",
            "name": "Coachella Valley Music and Arts Festival 2019 - Weekend 1",
            "fbEventId": "137943263736990",
            "participants": []
        }
    else:
        raise ValueError("unsupported event category: {}".format(event_category))

    d["locationRef"] = mock1["locationFirestoreRef"] if use_firestore_ref else mock1["locationRef"]

    return d


def getEventScheduleDict(toEvent=True):
    eventScheduleDict = {
        "destName": "LAX",
        "destTime": None,
        "flightTime": "2018-12-17T12:00:00.000",
        "memberProfilePhotoUrls": [],
        "pending": True,
        "rideRequestRef": mock1["rideRequestRef"],
        "locationRef": mock1["locationRef"],
        "orbitRef": None,

        # New fields for multiple event types
        "fbEventId": None

    }
    if toEvent:
        eventScheduleDict["toEvent"] = True
        eventScheduleDict["pickupAddress"] = "Tenaya Hall, San Diego, CA 92161"
    else:
        raise NotImplementedError

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

socialEventLocationDict = {
    'locationCategory': "social",
    'coordinates': {
        "latitude": 33.9416,
        "longitude": -118.4085
    },
    'address': "3150 Paradise Rd, Las Vegas, NV 89109",
    "eventName": "CES"
}


def getLocationDict(location_category="airport"):
    if location_category == "airport":
        return airportLocationDict
    elif location_category == "social":
        return socialEventLocationDict
    else:
        raise ValueError("unsupported location_category: {}".format(location_category))


def getLocation():
    locationDict = getLocationDict()
    location = Location.from_dict(locationDict, doc_id=mock1["locationId"])
    # location.set_firestore_ref(mock1["locationFirestoreRef"])
    return location


def getUserLocationDict():
    return {
        'locationCategory': "user",
        'coordinates': {'latitude': 32.8794203, 'longitude': -117.2428555},
        'address': 'Tenaya Hall, San Diego, CA 92161',
    }


def get_json_file(json_filename):
    with open('test/jsons_written_by_david_a/{}'.format(json_filename)) as json_file:
        return json.load(json_file)
