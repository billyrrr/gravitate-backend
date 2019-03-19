from unittest import TestCase
from gravitate.domain.driver_navigation.utils import get_address


class GetAddressTest(TestCase):
    def test_get_address(self):
        """
        TODO: switch to intended address (current address expected is not optimal)
        :return:
        """
        address = get_address({'latitude': 33.679974, 'longitude': -116.237221})
        self.assertEqual("Indio, CA, USA", address)

    def test_get_address_broad(self):
        """
        Tests that result_type=None removes restrictions on result_type
        :return:
        """
        address = get_address({'latitude': 33.679974, 'longitude': -116.237221}, result_type=None)
        self.assertNotEqual("", address, "Should return an address")
