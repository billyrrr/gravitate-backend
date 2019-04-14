import json
from unittest import TestCase, skip

from gravitate.forms.ride_request_creation_form import RideRequestCreationValidateForm
from test.store import FormDictFactory


class TestMockFormValidation(TestCase):

    @skip("Additional 'rideCategory' keyword in form required for new code. ")
    def testCreation(self):
        formDict = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)
        form: RideRequestCreationValidateForm = RideRequestCreationValidateForm(
            data=formDict)
        form.validate()
        self.assertDictEqual(formDict, form.data)

    def testPrintMockForm(self):
        formDict = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)
        print(json.dumps(formDict))

    def testValidate(self):
        formDict = FormDictFactory().create(hasEarliestLatest=False, returnDict=True)
        form: RideRequestCreationValidateForm = RideRequestCreationValidateForm(
            data=formDict)
        form.validate()
        self.assertEqual(form.validate(), True)