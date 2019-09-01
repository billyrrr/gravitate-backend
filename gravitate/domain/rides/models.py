"""Author: Zixuan Rao, Andrew Kim
"""
from gravitate.domain.location import Location
from gravitate.models.firestore_object import FirestoreObject
from gravitate.models.target import Target, ToEventTarget


class Ride(FirestoreObject):
    """ Description
        This class represents a RideRequest object

    """

    @staticmethod
    def from_dict_and_reference(ride_request_dict, ride_request_ref):
        ride_request = Ride.from_dict(ride_request_dict)
        ride_request.set_firestore_ref(ride_request_ref)
        return ride_request

    @staticmethod
    def from_dict(d):
        """ Description
            This function creates AirportRideRequest or SocialEventRideRequest.
                (RideRequest Factory)

            :param d:
        """
        ride_request_type = d['rideCategory']

        driver_status = d['driverStatus']
        # pickup_address = d['pickupAddress']
        origin_ref = d["originRef"]  # New
        destination_ref = d["destinationRef"]  # New
        has_checked_in = d['hasCheckedIn']
        event_ref = d['eventRef']
        orbit_ref = d['orbitRef']
        user_id = d['userId']
        target = Target.from_dict(d['target'])
        pricing = d['pricing']
        request_completion = d['requestCompletion']

        if ride_request_type == 'airportRide':
            flight_local_time = d['flightLocalTime']
            flight_number = d['flightNumber']
            airport_location = d['airportLocation']
            baggages = d['baggages']
            disabilities = d['disabilities']

            return AirportRide(driver_status, origin_ref, destination_ref, has_checked_in,
                               event_ref, orbit_ref, user_id, target, pricing, request_completion,
                               flight_local_time, flight_number, airport_location, baggages, disabilities)
        elif ride_request_type == 'eventRide':
            location_ref = d['locationRef']
            return SocialEventRide(driver_status, origin_ref, destination_ref, has_checked_in, event_ref, orbit_ref,
                                   user_id, target, pricing, request_completion, location_ref)
        else:
            raise Exception(
                'Not supported rideRequestType: {}'.format(ride_request_type))

    @property
    def pickup_address(self):
        return self._get_pickup_address()

    def _get_pickup_address(self):
        """
        Note that this method is non-transactional. We are assuming that
            Location objects are immutable and ready before the transaction.
        :return:
        """
        pickup_location_ref = None
        if self.target.to_event:
            pickup_location_ref = self.origin_ref
        else:
            raise ValueError("Pickup address of to_event=False is not supported. ")
        # if self._transaction is not None:
        #     location = LocationGenericDao().get_with_transaction(self._transaction, pickup_location_ref)
        #     return location.address
        # else:
        location = Location.get(pickup_location_ref.id)
        return location.address
        # warnings.warn("Using mock pickup address. Delete Before Release ")
        #
        # return "Tenaya Hall, San Diego, CA 92161"

    def _get_dropoff_address(self):
        dropoff_location_ref = None
        if not self.target.to_event:
            dropoff_location_ref = self.destination_ref
        else:
            raise ValueError("Pickup address of to_event=True is not supported. ")
        location = Location.get(dropoff_location_ref)
        return location.address

    def to_tuple_point(self, to_event = True):
        """ Returns a tuple (actually a list) representation of the ride request
            as a point for grouping algorithm.

        :return:
        """

        assert to_event is True

        # Time-related
        to_event_target: ToEventTarget = self.target
        earliest = to_event_target.arrive_at_event_time['earliest']
        latest = to_event_target.arrive_at_event_time['latest']

        # Tag to identify ride request
        ref = self.get_firestore_ref()

        # Location-related
        pickup_location_ref = None
        if self.target.to_event:
            pickup_location_ref = self.origin_ref
        else:
            raise ValueError("Pickup address of to_event=False is not supported. ")
        location = Location.get(pickup_location_ref)
        coordinates = location.coordinates
        latitude = coordinates["latitude"]
        longitude = coordinates["longitude"]

        # Form tuple ()
        t = [earliest, latest, latitude, longitude, ref]
        return t

    def to_dict(self):
        ride_request_dict = {
            'driverStatus': self.driver_status,
            'originRef': self.origin_ref,
            'destinationRef': self.destination_ref,
            # 'pickupAddress': self.pickup_address,
            'hasCheckedIn': self.has_checked_in,
            'eventRef': self.event_ref,
            'orbitRef': self.orbit_ref,
            'userId': self.user_id,
            'target': self.target.to_dict(),
            'pricing': self.pricing,
            'requestCompletion': self.request_completion
        }
        return ride_request_dict

    def to_dict_view(self):
        """
        Dict for external presentation / returns for endpoint get
        :return:
        """
        ride_request_dict = {
            'driverStatus': self.driver_status,
            'originId': self.origin_ref.id,
            'destinationId': self.destination_ref.id,
            'hasCheckedIn': self.has_checked_in,
            'eventId': self.event_ref.id,
            'orbitId': self.orbit_ref.id if self.orbit_ref is not None else None,
            'userId': self.user_id,
            'target': self.target.to_dict(),
            'pricing': self.pricing,
            'requestCompletion': self.request_completion
        }
        return ride_request_dict

    def __init__(self, driver_status, origin_ref, destination_ref, has_checked_in, event_ref, orbit_ref, user_id,
                 target, pricing, request_completion):
        """ Description
            This function initializes a RideRequest Object.
            Note that this function should not be called directly.

            :param self:
            :param driver_status:
            :param pickup_address:
            :param has_checked_in:
            :param event_ref:
            :param orbit_ref:
            :param target:
            :param pricing:
            :param request_completion:
        """

        super().__init__()
        self._transaction = None

        self.driver_status = driver_status
        self.origin_ref = origin_ref
        self.destination_ref = destination_ref
        # self.pickup_address = pickup_address
        self.has_checked_in = has_checked_in
        self.event_ref = event_ref
        self.orbit_ref = orbit_ref
        self.user_id = user_id
        self.target = target
        self.pricing = pricing
        self.request_completion = request_completion


class AirportRide(Ride):

    # TODO more arguments
    def __init__(self, driver_status, origin_ref, destination_ref, has_checked_in, event_ref, orbit_ref, user_id,
                 target, pricing,
                 request_completion, flight_local_time, flight_number, airport_location, baggages, disabilities):
        """ Description
            Initializes an AirportRideRequest Object
            Note that this class should not be initialzed directly.
            Use RideRequest.from_dict to create an AirportRideRequest.

            :param self:
            :param driver_status:
            :param pickup_address:
            :param has_checked_in:
            :param event_ref:
            :param orbit_ref:
            :param target:
            :param pricing:
            :param flight_local_time:
            :param flight_number:
            :param airport_location:
            :param baggages:
            :param disabilities:
        """

        super().__init__(driver_status, origin_ref, destination_ref,
                         has_checked_in, event_ref, orbit_ref, user_id, target, pricing, request_completion)
        self.ride_category = 'airportRide'
        self.flight_local_time = flight_local_time
        self.flight_number = flight_number
        self.airport_location = airport_location
        self.baggages = baggages
        self.disabilities = disabilities

    def to_dict(self):
        """ Description
            This function returns the dictionary representation of a RideRequest object
                so that it can be stored in the database.

        :type self:
        :param self:

        :raises:

        :rtype:
        """

        ride_request_dict = super().to_dict()

        ride_request_dict['rideCategory'] = 'airportRide'
        ride_request_dict['flightLocalTime'] = self.flight_local_time
        ride_request_dict['flightNumber'] = self.flight_number
        ride_request_dict['airportLocation'] = self.airport_location
        ride_request_dict['baggages'] = self.baggages
        ride_request_dict['disabilities'] = self.disabilities
        return ride_request_dict

    def to_dict_view(self):
        ride_request_dict = super().to_dict_view()

        ride_request_dict['rideCategory'] = 'airportRide'
        ride_request_dict['flightLocalTime'] = self.flight_local_time
        ride_request_dict['flightNumber'] = self.flight_number
        ride_request_dict['locationId'] = self.airport_location.id
        ride_request_dict['baggages'] = self.baggages
        ride_request_dict['disabilities'] = self.disabilities
        return ride_request_dict


class SocialEventRide(Ride):

    # TODO more arguments
    def __init__(self, driver_status, origin_ref, destination_ref, has_checked_in, event_ref, orbit_ref, user_id,
                 target, pricing,
                 request_completion, location_ref):
        """ Description
            Initializes a SocialEventRideRequest Object
            Note that this class should not be initialized directly.
            Use RideRequest.from_dict to create a SocialEventRideRequest.

        :type self:
        :param self:

        :type dictionary:
        :param dictionary:

        :raises:

        :rtype:
        """

        super().__init__(driver_status, origin_ref, destination_ref,
                         has_checked_in, event_ref, orbit_ref, user_id, target, pricing, request_completion)
        self.location_ref = location_ref
        self.ride_category = 'eventRide'

    def to_dict(self):
        ride_request_dict = super().to_dict()
        ride_request_dict['rideCategory'] = 'eventRide'
        ride_request_dict['locationRef'] = self.location_ref

        return ride_request_dict

    def to_dict_view(self):
        ride_request_dict = super().to_dict_view()

        ride_request_dict['rideCategory'] = 'eventRide'
        ride_request_dict['locationId'] = self.location_ref.id

        return ride_request_dict
