import warnings

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


def pair(arr=None) -> (list, list):
    """
    Description

        Author: Tyler

        :param arr:  an array of ride requests
            [the first is earliest allowable time, second is latest time, third is firestore reference]
        :param paired:
        :param unpaired:
    """

    paired = list()
    unpaired = list()

    sortedArr = sorted(arr, key=lambda x: x[0])

    i = 0
    while i < len(sortedArr):

        if i == len(sortedArr) - 1:
            unpaired.insert(len(unpaired), [sortedArr[i][2]])
            i += 1
        else:
            if (sortedArr[i][1] >= sortedArr[i + 1][0]):

                paired.insert(len(paired), [sortedArr[i][2], sortedArr[i + 1][2]])
                i += 1
            else:

                unpaired.insert(len(unpaired), [sortedArr[i][2]])
            i += 1
    return paired, unpaired
