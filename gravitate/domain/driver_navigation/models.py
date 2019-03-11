from gravitate.models import Orbit


class DriverNavigation:

    def from_dict(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def __init__(self):
        raise NotImplementedError


def build_driver_navigation_from_orbit(orbit: Orbit) :
    """ Returns a DriverNavigation that briefs the driver of all pickup addresses and their order.

    :param orbit:
    :return:
    """
    raise NotImplementedError
