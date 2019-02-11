from unittest import TestCase

from gravitate import models, data_access
from gravitate.domain.request_ride.builders import RideRequestBaseBuilder, SocialEventRideRequestBuilder
from test import context, store
from test.store import FormDictFactory

db = context.Context.db


class RideRequestDictBuilderTest(TestCase):

    def testSetVariables(self):
        userId = 'testuserid1'
        d = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)

        b = RideRequestBaseBuilder().set_data(
            user_id=userId, flight_local_time=d["flightLocalTime"], flight_number=d["flightNumber"],
            # pricing=d["pricing"],  # diabilities=d["disabilities"], baggages=d["baggages"],
            airport_code=d["airportCode"], to_event=d["toEvent"], pickup_address=d["pickupAddress"],
            driver_status=d["driverStatus"]
        )
        expected_vars = {'user_id': 'testuserid1',
                         'flight_local_time': '2018-12-17T12:00:00.000', 'flight_number': 'DL89',
                         'airport_code': 'LAX',
                         'pickup_address': 'Tenaya Hall, San Diego, CA 92161',
                         'driver_status': False,
                         'to_event': True,
                         }
        # Assert that all required variables are set
        self.assertTrue(expected_vars.items() <= vars(b).items())


class SocialEventDictBuilderTest(TestCase):
    builder: SocialEventRideRequestBuilder = None

    def setUp(self):
        self.refs_to_delete = list()

    def testSetWithForm(self):
        userId = 'testuserid1'
        d = store.EventRideRequestFormDictFactory().create()

        b = SocialEventRideRequestBuilder().set_with_form_and_user_id(d, user_id=userId)
        expected_vars = {'user_id': 'testuserid1',
                         'event_id': 'testformeventid1',
                         'pickup_address': 'Tenaya Hall, San Diego, CA 92161',
                         'driver_status': False,
                         'to_event': True
                         }
        # Assert that all required variables are set
        print(vars(b))
        self.assertTrue(expected_vars.items() <= vars(b).items())

    def testBuild(self):
        def setUp(self):
            event_dict = store.getEventDict(event_category="social")
            event = models.Event.from_dict(event_dict)
            event_ref = data_access.EventDao().create(event)
            self.refs_to_delete.append(event_ref)
            self.event_id = event_ref.id
            d = store.EventRideRequestFormDictFactory().create(event_id=self.event_id)
            self.user_id = 'testuserid1'
            self.builder: SocialEventRideRequestBuilder = \
                SocialEventRideRequestBuilder().set_with_form_and_user_id(d, user_id=self.user_id)
        setUp(self)
        self.builder.build_social_event_ride_request()
        _d_expected = {
            'rideCategory': 'eventRide',
            'pickupAddress': "Tenaya Hall, San Diego, CA 92161",
            'driverStatus': False,
            'orbitRef': None,
            'target': {'eventCategory': 'eventRide',
                       'toEvent': True,
                       'arriveAtEventTime':
                           {'earliest': 1545033600, 'latest': 1545119999}},
            'eventRef': db.document('events', self.event_id),
            'userId': self.user_id,
            'hasCheckedIn': False,
            'pricing': 987654321,
            "baggages": dict(),
            "disabilities": dict(),

            "requestCompletion": False
        }
        # self.assertTrue(_d_expected.items() <= self.builder._ride_request_dict.items())
        self.assertDictContainsSubset(_d_expected, self.builder._ride_request_dict)

    def tearDown(self):
        for ref in self.refs_to_delete:
            ref.delete()
        self.refs_to_delete.clear()
