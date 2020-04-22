from tests.utils import _delete_all


def pytest_sessionstart(session):
    from flask_boiler.context import Context as CTX
    from flask_boiler.config import Config

    if CTX.config is None:
        CTX.load()

    _delete_all(CTX, "Orbit")
    _delete_all(CTX, "events")
    _delete_all(CTX, "locations")
    _delete_all(CTX, "orbits")
    _delete_all(CTX, "rideHosts")
    _delete_all(CTX, "riderBookings")
    _delete_all(CTX, "riderTargets")
    _delete_all(CTX, "users")

    _delete_all(CTX, subcollection_name="bookings_POST")
    _delete_all(CTX, subcollection_name="locations_POST")
    _delete_all(CTX, subcollection_name="sublocations_POST")

    _delete_all(CTX, subcollection_name="bookings")
    _delete_all(CTX, subcollection_name="locations")
    _delete_all(CTX, subcollection_name="sublocations")


def pytest_sessionfinish(session, exitstatus):
    from flask_boiler.context import Context as CTX

    if exitstatus == 0:
        _delete_all(CTX, "Orbit")
        _delete_all(CTX, "events")
        _delete_all(CTX, "locations")
        _delete_all(CTX, "orbits")
        _delete_all(CTX, "rideHosts")
        _delete_all(CTX, "riderBookings")
        _delete_all(CTX, "riderTargets")
        _delete_all(CTX, "users")

        _delete_all(CTX, subcollection_name="bookings_POST")
        _delete_all(CTX, subcollection_name="locations_POST")
        _delete_all(CTX, subcollection_name="sublocations_POST")

        _delete_all(CTX, subcollection_name="bookings")
        _delete_all(CTX, subcollection_name="locations")
        _delete_all(CTX, subcollection_name="sublocations")
