from unittest import TestCase
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
