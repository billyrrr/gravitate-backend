from gravitate.domain.location import models
from unittest import TestCase


class UserLocationModelTest(TestCase):

    def test_from_dict(self):

        d = {
            'obj_type': "UserLocation",
            'coordinates': {'latitude': 32.8794203,
                                'longitude': -117.2428555},
            'address': 'Tenaya Hall, San Diego, CA 92161',
        }

        obj = models.UserLocation.from_dict(d, doc_id=None)

        self.assertDictEqual(obj.coordinates, {'latitude': 32.8794203,
                                'longitude': -117.2428555})
        self.assertEqual(obj.address, 'Tenaya Hall, San Diego, CA 92161')
        self.assertTrue(isinstance(obj, models.UserLocation))


class AirportLocationModelTest(TestCase):

    def test_from_dict(self):
        d = {
            'obj_type': "AirportLocation",
            'coordinates': {
                "latitude": 33.9416,
                "longitude": -118.4085
            },
            'address': "1 World Way, Los Angeles, CA 90045",
            'airportCode': "LAX",
        }
        obj = models.AirportLocation.from_dict(d, doc_id=None)
        self.assertDictEqual(obj.coordinates, {
            "latitude": 33.9416,
            "longitude": -118.4085
        })
        self.assertEqual(obj.address, "1 World Way, Los Angeles, CA 90045")
        self.assertEqual(obj.airport_code, "LAX")
        self.assertTrue(isinstance(obj, models.AirportLocation))


class SocialEventLocationModelTest(TestCase):

    def test_from_dict(self):
        d = {
            'obj_type': "SocialEventLocation",
            'coordinates': {
                "latitude": 33.9416,
                "longitude": -118.4085
            },
            'address': "3150 Paradise Rd, Las Vegas, NV 89109",
            "eventName": "CES"
        }
        obj = models.SocialEventLocation.from_dict(d, doc_id=None)
        self.assertDictEqual(obj.coordinates, {
                "latitude": 33.9416,
                "longitude": -118.4085
            })
        self.assertEqual(obj.address, "3150 Paradise Rd, Las Vegas, NV 89109")
        print(obj.schema_obj.fields.keys())
        print(vars(obj))
        self.assertEqual(obj.event_name, "CES")
        self.assertTrue(isinstance(obj, models.SocialEventLocation))

    def test_from_fb_place(self):
        fb_d = {
            "name": "Coachella",
            "location": {
                "latitude": 33.679974,
                "longitude": -116.237221
            },
            "id": "20281766647"
        }
        location = models.LocationFactory.from_fb_place(fb_d)
        self.assertDictEqual(location.coordinates, {
                "latitude": 33.679974,
                "longitude": -116.237221
            }
        )
        self.assertEqual(location.event_name, 'Coachella')
        self.assertTrue(isinstance(location, models.SocialEventLocation))
        self.assertEqual(location.address, 'Indio, CA, USA')
