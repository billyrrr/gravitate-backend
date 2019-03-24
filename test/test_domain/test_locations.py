from unittest import TestCase

from gravitate.models import SocialEventLocation
from gravitate.models.location import Location


class LocationModelTest(TestCase):

    def test_location_factory(self):
        location = Location.from_pickup_address('Tenaya Hall, San Diego, CA 92161')
        location_dict = {
            'locationCategory': "user",
            'coordinates': {'latitude': 32.8794203, 'longitude': -117.2428555},
            'address': 'Tenaya Hall, San Diego, CA 92161',
        }
        self.assertDictEqual(location.to_dict(), location_dict)


class EventLocationTest(TestCase):

    def test_from_facebook_place(self):
        fb_d = {
            "name": "Coachella",
            "location": {
                "latitude": 33.679974,
                "longitude": -116.237221
            },
            "id": "20281766647"
        }
        location = SocialEventLocation.from_fb_place(fb_d)
        result = location.to_dict()
        expected_d = {
            'locationCategory': "social",
            'coordinates': {
                "latitude": 33.679974,
                "longitude": -116.237221
            },
            'eventName': 'Coachella',
            'address': 'Indio, CA, USA',
        }
        self.assertDictEqual(expected_d, result)
