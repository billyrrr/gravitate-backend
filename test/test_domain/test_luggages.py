from gravitate.domain.luggages import Luggages
from unittest import TestCase


class LuggagesTest(TestCase):

    def setUp(self):
        luggage_a = {
            "luggage_type": "large",
            "weight_in_lbs": 20
        }

        luggage_b = {
            "luggage_type": "medium",
            "weight_in_lbs": 15
        }

        luggage_c = {
            "luggage_type": "medium",
            "weight_in_lbs": 25
        }

        luggage_d = {
            "luggage_type": "small",
            "weight_in_lbs": 5
        }

        self.luggage_list = [luggage_a, luggage_b, luggage_c, luggage_d]

    def test_init(self):
        """
        Tests that Luggages class initializes successfully with no argument
        :return:
        """
        luggages = Luggages()
        self.assertIsNotNone(luggages, msg="Luggages did not initialize. ")

    def test_add_one(self):
        luggages = Luggages()
        luggages.add(self.luggage_list[0])
        self.assertListEqual(luggages._luggage_list, [self.luggage_list[0]])

    def test_add_many(self):
        luggages = Luggages()
        for luggage in self.luggage_list:
            luggages.add(luggage)
        self.assertListEqual(luggages._luggage_list, self.luggage_list)

    def test_get_count(self):
        """ Tests that Luggages class counts luggages correctly.

        :return:
        """
        luggages = Luggages()
        for luggage in self.luggage_list:
            luggages.add(luggage)
        self.assertEqual(luggages._get_count(), len(self.luggage_list))

    def test_get_count_one(self):
        luggages = Luggages()
        luggages.add(self.luggage_list[0])
        self.assertEqual(luggages._get_count(), 1)

    def test_get_weight_one(self):
        luggages = Luggages()
        luggages.add(self.luggage_list[0])
        self.assertEqual(luggages._get_weight(), 20)

    def test_to_dict_one_pcs(self):
        """
        Tests that Luggages successfully returns dict with correct count and weight.
        :return:
        """
        luggages = Luggages()
        luggages._luggage_list = self.luggage_list[0]
        expected_dict = {
            "luggages": [
                {
                    "luggage_type": "large",
                    "weight_in_lbs": 20
                }
            ],
            "total_weight": 20,
            "total_count": 1
        }
        self.assertDictEqual(expected_dict, luggages.to_dict(), "Luggages did not return correct dict")

    def test_to_dict_two_pcs(self):
        luggages = Luggages()
        luggages._luggage_list = [self.luggage_list[0], self.luggage_list[1]]
        expected_dict = {
            "luggages": [
                {
                    "luggage_type": "large",
                    "weight_in_lbs": 20
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 15
                }
            ],
            "total_weight": 35,
            "total_count": 2
        }
        self.assertDictEqual(expected_dict, luggages.to_dict(), "Luggages did not return correct dict")

    def test_to_dict_many_pcs(self):
        luggages = Luggages()
        luggages._luggage_list = [self.luggage_list[0], self.luggage_list[1], self.luggage_list[2]]
        expected_dict = {
            "luggages": [
                {
                    "luggage_type": "large",
                    "weight_in_lbs": 20
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 15
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 25
                }
            ],
            "total_weight": 60,
            "total_count": 3
        }
        self.assertDictEqual(expected_dict, luggages.to_dict(), "Luggages did not return correct dict")





