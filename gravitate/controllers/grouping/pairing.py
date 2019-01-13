import warnings

from gravitate.controllers.grouping.paring import pair
from gravitate.models import ToEventTarget


def pair_ride_requests(ride_requests: list):
    """
    This function serves as an adaptor for grouping algorithms.
    :param ride_requests:
    :return:
    """
    tuple_list = construct_tuple_list(ride_requests)
    paired, unpaired = pair(arr=tuple_list)
    return paired, unpaired


def construct_tuple_list(ride_requests: list):
    """ Description
        This function constructs tuple list consisting only variables relevant to the
            grouping algorithm.
        Note that this function only supports rideRequests with ToEventTarget as Target.

        :type ride_requests:list:
        :param ride_requests:list:

        :raises:

        :rtype:
    """
    arr = list()

    for ride_request in ride_requests:
        try:
            to_event_target: ToEventTarget = ride_request.target
            earliest = to_event_target.arrive_at_event_time['earliest']
            latest = to_event_target.arrive_at_event_time['latest']
            ref = ride_request.get_firestore_ref()
            tuple_to_append = [earliest, latest, ref]
            arr.append(tuple_to_append)
        except Exception as e:
            warnings.warn("failed to parse rideRequest: {}".format(ride_request.to_dict()))
            print("error: {}".format(e))

    return arr