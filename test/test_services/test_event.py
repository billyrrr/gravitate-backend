import unittest

from google.cloud import firestore

from gravitate import main as main
from gravitate.data_access import LocationGenericDao
from gravitate.domain.event.dao import EventDao
from gravitate.domain.event.models import Event
from gravitate.models import Location
from test import scripts
from test.store import getEventDict, getLocationDict
from test.test_main import getMockAuthHeaders


class UserEventServiceTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()

    def test_put_many(self):
        fb_dicts = { "data": [
            {
                "description": "Pool season will be back in session from June 7-9 for Splash House 2019 💦\n\nPackages and early bird pre-sale begins Wed, 2/6 at 12PM PT at www.splashhouse.com \n21+\n\nJune 7 / 8 / 9\nPalm Springs, CA\nBringing the best house music to 3 resorts:\nRenaissance Palm Springs Hotel\nThe Riviera Palm Springs, A Tribute Portfolio Resort\nThe Saguaro Palm Springs\n+\nAfter Hours at Palm Springs Air Museum",
                "end_time": "2019-06-09T23:00:00-0700",
                "name": "Splash House June 2019",
                "place": {
                    "name": "Palm Springs",
                    "location": {
                        "city": "Palm Springs",
                        "country": "United States",
                        "latitude": 33.8443,
                        "longitude": -116.5279,
                        "state": "CA",
                        "zip": "92262–92264"
                    },
                    "id": "108231342537990"
                },
                "start_time": "2019-06-07T12:00:00-0700",
                "id": "531366380703501",
                "rsvp_status": "unsure"
            },
            {
                "description": "Goldenvoice presents\nThe Cure to Loneliness Tour\n\nJAI WOLF\nwith shallou\n\nSAT, 1 JUN 2019 at 09:00PM PDT\nAges: 18 & Over\nDoors Open: 08:00PM\n\nOnSale: Fri, 18 Jan 2019 at 10:00AM PST\nAnnouncement: Mon, 14 Jan 2019 at 10:00AM PST\n\n2nd show added for Fri, 5/31. Tickets available HERE",
                "name": "Jai Wolf",
                "place": {
                    "name": "Shrine Auditorium & Expo Hall",
                    "location": {
                        "city": "Los Angeles",
                        "country": "United States",
                        "latitude": 34.023527532076,
                        "longitude": -118.28130708212,
                        "state": "CA",
                        "street": "665 W Jefferson Blvd",
                        "zip": "90007"
                    },
                    "id": "81721568089"
                },
                "start_time": "2019-06-01T21:00:00-0700",
                "id": "284909175532434",
                "rsvp_status": "unsure"
            },
            {
                "description": "91X, Z90 & Magic 92.5 presents 2019 SoCal TACO FEST!   \n\nThe event will take place on Saturday, May 18th at Waterfront Park in downtown San Diego, with over 25 of your favorite restaurants for San Diego’s BIGGEST taco festival! Plus, live Lucha Libre wrestling, Chihuahua races & beauty pageant, and a bumpin’ Margarita Tent!\n\nWith a music lineup featuring:\nNelly\nSuper Diamond\nArise Roots\nDJ D-ROCK\nand more TBA!\n\nTICKETS ARE ON SALE NOW:\nhttps://tickets.socaltacofest.com/e/socal-taco-fest/tickets\n\n2019 SoCal TACO FEST is 21+ and up only.\n\n@SoCalTacoFest on Twitter & Instagram!",
                "end_time": "2019-05-18T22:00:00-0700",
                "name": "SoCal TACO FEST 2019",
                "place": {
                    "name": "Waterfront Park",
                    "location": {
                        "city": "San Diego",
                        "country": "United States",
                        "latitude": 32.72199,
                        "longitude": -117.17205,
                        "state": "CA",
                        "street": "1600 Pacific Hwy",
                        "zip": "92101"
                    },
                    "id": "1714199095465525"
                },
                "start_time": "2019-05-18T11:00:00-0700",
                "id": "312156202757788",
                "rsvp_status": "unsure"
            },
            {
                "description": "49th Celebration Day",
                "name": "Santana pa Ti Live / Chicano Park",
                "place": {
                    "name": "Chicano Park",
                    "location": {
                        "city": "San Diego",
                        "country": "United States",
                        "latitude": 32.700194037186,
                        "longitude": -117.14327617597,
                        "state": "CA",
                        "street": "National Ave",
                        "zip": "92113"
                    },
                    "id": "119225144790924"
                },
                "start_time": "2019-04-20T12:00:00-0700",
                "id": "441105913093298",
                "rsvp_status": "attending"
            },
            {
                "description": "The 49th annual Chicano Park Day celebration will be held on Saturday, April 20, 2019. The annual celebration is held in historic Chicano Park, located in the Logan Heights community, south of downtown San Diego under the San Diego-Coronado bridge. \n\nThe theme for the 2019 celebration is 'Danzantes, Protectors of Our Traditions and Chicano Park, 500 Years of Anti-Colonial Struggle.'\n\nThis family event is always free and open to the public.\n\nThe celebration will include Aztec Indigenous dance, coordinated by coordinated by Danza Azteca Calpulli Mexihca, live bands on two stages, ballet folklórico and other danza groups and speakers. In addition, there were kids arts workshops, a display of classic lowrider cars coordinated by Amigos Car Club, speakers, and various food, arts & crafts, and informational booths.\n\n*NO ALCOHOL and NO PETS, other than service animals are allowed at the event. Thank you for your cooperation.*\n\nPublic transportation: Take the blue line trolley to the Barrio Logan station or the orange line to 25th and Commercial. For alternate routes, go to www.sdmts.com/Tripplanner.asp",
                "end_time": "2019-04-20T17:00:00-0700",
                "name": "49th Chicano Park Day Celebration",
                "place": {
                    "name": "Chicano Park",
                    "location": {
                        "city": "San Diego",
                        "country": "United States",
                        "latitude": 32.700194037186,
                        "longitude": -117.14327617597,
                        "state": "CA",
                        "street": "National Ave",
                        "zip": "92113"
                    },
                    "id": "119225144790924"
                },
                "start_time": "2019-04-20T10:00:00-0700",
                "id": "291514501708008",
                "rsvp_status": "unsure"
            },
            {
                "description": "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com",
                "end_time": "2019-04-14T23:59:00-0700",
                "name": "Coachella Valley Music and Arts Festival 2019 - Weekend 1",
                "place": {
                    "name": "Coachella",
                    "location": {
                        "latitude": 33.679974,
                        "longitude": -116.237221
                    },
                    "id": "20281766647"
                },
                "start_time": "2019-04-12T12:00:00-0700",
                "id": "137943263736990",
                "rsvp_status": "unsure"
            },
            {
                "description": "El Gordo Viclas present Ay Guey Custom Viclas",
                "name": "Day at the Bay Viclas and Car Show",
                "place": {
                    "name": "Embarcadero Marina Park South",
                    "location": {
                        "city": "San Diego",
                        "country": "United States",
                        "latitude": 32.704328082064,
                        "located_in": "358290337510",
                        "longitude": -117.16464887991,
                        "state": "CA",
                        "street": "111 W Harbor Dr",
                        "zip": "92101"
                    },
                    "id": "2042612439087865"
                },
                "start_time": "2019-04-07T23:10:00-0700",
                "id": "629428087472698",
                "rsvp_status": "unsure"
            }
        ] }
        r = self.app.put(path='/me/events',
                         headers=getMockAuthHeaders(),
                         json=fb_dicts
                         )
        result = r.json
        self.assertDictEqual(result,
                             {
                                 "ids": [
                                     "531366380703501",
                                     "284909175532434",
                                     "312156202757788",
                                     "441105913093298",
                                     "291514501708008",
                                     "137943263736990",
                                     "629428087472698"
                                 ]
                             })

    def test_post(self):
        fb_dict = {
            "description": "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com",
            "end_time": "2019-04-14T23:59:00-0700",
            "name": "Coachella Valley Music and Arts Festival 2019 - Weekend 1",
            "place": {
                "name": "Coachella",
                "location": {
                    "latitude": 33.679974,
                    "longitude": -116.237221
                },
                "id": "20281766647"
            },
            "start_time": "2019-04-12T12:00:00-0700",
            "id": "137943263736990"
        }
        r = self.app.post(path='/me/events',
                          headers=getMockAuthHeaders(),
                          json=fb_dict
                          )
        result = r.json
        print(result)

    def test_post_twice(self):
        """
        Test that posting the same event twice returns the same id
        :return:
        """
        fb_dict = {
            "description": "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com",
            "end_time": "2019-04-14T23:59:00-0700",
            "name": "Coachella Valley Music and Arts Festival 2019 - Weekend 1",
            "place": {
                "name": "Coachella",
                "location": {
                    "latitude": 33.679974,
                    "longitude": -116.237221
                },
                "id": "20281766647"
            },
            "start_time": "2019-04-12T12:00:00-0700",
            "id": "137943263736990"
        }
        r = self.app.post(path='/me/events',
                          headers=getMockAuthHeaders(),
                          json=fb_dict
                          )
        result = r.json
        id_1 = result["id"]
        r = self.app.post(path='/me/events',
                          headers=getMockAuthHeaders(),
                          json=fb_dict
                          )
        result = r.json
        id_2 = result["id"]
        self.assertEqual(id_1, id_2)


class EventServiceTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):

        self.refs_to_delete = list()

        event_dict = getEventDict(use_firestore_ref=True,
                                  to_earliest=1545033600,
                                  to_latest=1545119999,
                                  from_earliest=1545033600,
                                  from_latest=1545119999)

        # Populate location
        location_ref = event_dict["locationRef"]
        location_d = getLocationDict(location_category="social")
        location = Location.from_dict(location_d)
        LocationGenericDao().set(location, location_ref)
        self.refs_to_delete.append(location_ref)

        self.event = Event.from_dict(event_dict)

        main.app.testing = True
        self.app = main.app.test_client()
        self.userId = "testuid1"

        self.c = scripts.SetUpTestDatabase()
        self.c.clear_before()
        self.c.generate_test_data(start_string="2018-12-17T08:00:00.000", num_days=5)

        event_ref: firestore.DocumentReference = EventDao().create(self.event)
        self.event.set_firestore_ref(event_ref)
        self.refs_to_delete.append(event_ref)
        self.event_id = event_ref.id

    def testGet(self):
        """
        Note that test data generated by getEventDict has a 9AM-11AM range
        :return:
        """
        r = self.app.get(path='/events' + '/' + self.event_id,
                         headers=getMockAuthHeaders()
                         )

        dict_expected = {
            'eventCategory': "airport",
            'participants': [],
            'airportCode': "LAX",
            'earliestArrival': "2018-12-17T00:00:00",
            'earliestDeparture': '2018-12-17T00:00:00',
            'latestArrival': "2018-12-17T23:59:59",
            'latestDeparture': "2018-12-17T23:59:59",
            'pricing': 100,
            'locationId': "testairportlocationid1",
            'isClosed': False
        }

        result = dict(r.json)

        self.assertEqual(r.status_code, 200, "GET is successful")
        # print(result)
        self.assertDictContainsSubset(dict_expected, result)

    def tearDown(self):
        for ref in self.refs_to_delete:
            ref.delete()
        self.refs_to_delete.clear()
        self.c.clear_after()
