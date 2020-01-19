"""
Instruction: run LuggagesTest in your IDE. Run test_context first to show that your environment is configured
    correctly.
"""

from unittest import TestCase, skip

from gravitate.domain.luggage_new.models import Luggages, LuggageItem


# @skip
class LuggageItemTest(TestCase):

    def setUp(self):
        luggage_a = {
            "luggage_type": "large",
            "weight_in_lbs": 20
        }
        self.luggage = luggage_a

    def test_from_dict(self):
        luggage_item = LuggageItem.new(**self.luggage)

        def assert_luggage_equal(a: LuggageItem, b: LuggageItem):
            assert a.luggage_type == b.luggage_type
            assert a.weight_in_lbs == b.weight_in_lbs

        expected = LuggageItem()
        expected.weight_in_lbs = 20
        expected.luggage_type = "large"

        assert_luggage_equal(expected, luggage_item)


# @skip("not yet implemented. Comment this decorator when test is needed")
@skip
class LuggagesTest(TestCase):

    def setUp(self):
        id_a = "luggage_id_0"
        d_a = {
            "luggage_type": "large",
            "weight_in_lbs": 20,
            "doc_id": id_a  # abnormal usage
        }
        luggage_a = LuggageItem.from_dict( d_a, doc_id=id_a)
        luggage_a.save()

        id_b = "luggage_id_1"
        d_b = {
            "luggage_type": "medium",
            "weight_in_lbs": 15,
            "doc_id": id_b  # abnormal usage
        }
        luggage_b = LuggageItem.from_dict( d_b, doc_id=id_b )
        luggage_b.save()

        id_c = "luggage_id_2"
        d_c = {
            "luggage_type": "medium",
            "weight_in_lbs": 25,
            "doc_id": id_c  # abnormal usage
        }
        luggage_c = LuggageItem.from_dict( d_c, doc_id=id_c )
        luggage_c.save()

        id_d = "luggage_id_3"
        d_d = {
            "luggage_type": "small",
            "weight_in_lbs": 5,
            "doc_id": id_d  # abnormal usage
        }
        luggage_d = LuggageItem.from_dict( d_d, doc_id=id_d )
        luggage_d.save()

        self.luggage_d_list = [d_a, d_b, d_c, d_d]
        self.luggage_list = [luggage_a, luggage_b, luggage_c, luggage_d]

    def test_context(self):
        self.assertTrue("Context set up correctly")

    def test_init(self):
        """
        Tests that Luggages class initializes successfully with no argument
        :return:
        """
        luggages = Luggages()
        self.assertIsNotNone(luggages, msg="Luggages did not initialize. ")

    def test_add_one(self):
        luggages = Luggages()
        luggages.set("luggage_id_0", self.luggage_list[0])
        self.assertListEqual(luggages.luggages, [self.luggage_list[0]])

    def test_add_many(self):
        luggages = Luggages()
        for idx in range(len(self.luggage_list)):
            luggage = self.luggage_list[idx]
            luggages.set("luggage_id_{}".format(idx), luggage)
        self.assertListEqual(luggages.luggages, self.luggage_list)

    def test_get_count(self):
        """ Tests that Luggages class counts luggages correctly.

        :return:
        """
        luggages = Luggages()
        for idx in range(len(self.luggage_list)):
            luggage = self.luggage_list[idx]
            luggages.set("luggage_id_{}".format(idx), luggage)
        self.assertEqual(luggages._get_count(), len(self.luggage_list))

    def test_get_count_one(self):
        luggages = Luggages()
        luggages.set("luggage_id_0", self.luggage_list[0])
        self.assertEqual(luggages._get_count(), 1)

    def test_get_weight_one(self):
        luggages = Luggages()
        luggages.set("luggage_id_0", self.luggage_list[0])
        self.assertEqual(luggages._get_weight(), 20)

    def test_to_dict_one_pcs(self):
        """
        Tests that Luggages successfully returns dict with correct count and weight.
        :return:
        """
        luggages = Luggages()
        luggages.set("luggage_id_0", self.luggage_list[0])
        expected_dict = {
            "luggages": [
                {
                    # "doc_id": "luggage_id_0",
                    "luggage_type": "large",
                    "weight_in_lbs": 20,
                    # 'obj_type': 'LuggageItem'
                }
            ],
            "total_weight": 20,
            "total_count": 1
        }
        self.assertDictEqual(expected_dict, luggages.to_dict(),
                             "Luggages did not return correct dict")

    def test_to_view_dict_one_pcs(self):
        """
        Tests that Luggages successfully returns view dict with correct count and weight.
        :return:
        """
        luggages = Luggages()
        luggages.set("luggage_id_0", self.luggage_list[0])
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
        self.assertDictEqual(expected_dict, luggages.to_view_dict(),
                             "Luggages did not return correct view dict")

    def test_to_dict_two_pcs(self):
        luggages = Luggages()
        luggages.set("luggage_id_0", self.luggage_list[0])
        luggages.set("luggage_id_1", self.luggage_list[1])
        expected_dict = {
            "luggages": [
                {
                    "luggage_type": "large",
                    "weight_in_lbs": 20,
                    # 'obj_type': 'LuggageItem'
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 15,
                    # 'obj_type': 'LuggageItem'
                }
            ],
            "total_weight": 35,
            "total_count": 2
        }
        self.assertDictEqual(expected_dict, luggages.to_dict(),
                             "Luggages did not return correct dict")

    def test_to_dict_many_pcs(self):
        luggages = Luggages()
        luggages.set("luggage_id_0", self.luggage_list[0])
        luggages.set("luggage_id_1", self.luggage_list[1])
        luggages.set("luggage_id_2", self.luggage_list[2])
        expected_dict = {
            "luggages": [
                {
                    "luggage_type": "large",
                    "weight_in_lbs": 20,
                    # 'obj_type': 'LuggageItem'
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 15,
                    # 'obj_type': 'LuggageItem'
                },
                {
                    "luggage_type": "medium",
                    "weight_in_lbs": 25,
                    # 'obj_type': 'LuggageItem'
                }
            ],
            "total_weight": 60,
            "total_count": 3
        }
        self.assertDictEqual(expected_dict, luggages.to_dict(),
                             "Luggages did not return correct dict")

    @skip
    def test_from_dict(self):
        d = {
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
        luggages = Luggages.from_dict(d)
        self.assertListEqual(luggages._luggage_list,
                             [self.luggage_list[0], self.luggage_list[1]])
