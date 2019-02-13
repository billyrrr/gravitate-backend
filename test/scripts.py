from gravitate import scripts
from gravitate import models
from gravitate import data_access
from gravitate.domain.group import actions as group_actions
from test import store
from typing import Type
from gravitate import context

CTX = context.Context
db = CTX.db


def generate_test_data():
    scripts.populate_locations.doWork()
    scripts.populate_airport_events.populate_events(start_string="2018-12-01T08:00:00.000", num_days=35)


def generate_ride_request() -> Type[models.RideRequest]:
    ride_request_dict = store.getMockRideRequest(returnDict=True)
    ride_request = models.RideRequest.from_dict(ride_request_dict)
    data_access.RideRequestGenericDao().create(ride_request)
    data_access.RideRequestGenericDao().set(ride_request)
    # ref = ride_request.get_firestore_ref()
    return ride_request


def generate_orbit(event_ref) -> models.Orbit:
    orbit_dict = store.get_orbit_dict_empty(event_ref)
    orbit = models.Orbit.from_dict(orbit_dict)
    data_access.OrbitDao().create(orbit)
    return orbit


def remove_match_tmp(ride_request_id):
    ride_request_ref = data_access.RideRequestGenericDao().rideRequestCollectionRef.document(ride_request_id)
    ride_request = data_access.RideRequestGenericDao().get(ride_request_ref)
    orbit_ref = ride_request.orbit_ref
    orbit = data_access.OrbitDao().get(orbit_ref)
    group_actions.remove_from_orbit(ride_request, orbit)


class SetUpTestDatabase:

    def __init__(self):
        self.refs_to_delete = list()

    @staticmethod
    def clear_before():
        """ Delete all events and locations before test
        :return:
        """
        scripts.delete_all_events()
        scripts.delete_all_locations()

    def generate_test_data(self,
                           airport_code="LAX", start_string="2018-12-07T08:00:00.000",
                           num_days=3, event_category="airport"):
        """
        Generate data needed by the test
        :param airport_code:
        :param start_string:
        :param num_days:
        :param event_category:
        :return:
        """
        c = scripts.populate_locations.PopulateLocationCommand(airport_code=airport_code)
        refs = c.execute()
        self.refs_to_delete.extend(refs)
        c = scripts.populate_airport_events.PopulateEventCommand(
            start_string=start_string, num_days=num_days, event_category=event_category)
        refs = c.execute()
        self.refs_to_delete.extend(refs)

    def clear_after(self):
        for ref in self.refs_to_delete:
            ref.delete()


if __name__ == "__main__":
    scripts.delete_all_events()
    scripts.delete_all_locations()
    generate_test_data()
