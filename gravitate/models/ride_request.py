"""Author: Zixuan Rao, Andrew Kim
"""

from google.cloud.firestore import DocumentReference, Transaction
from gravitate.models.target import Target, ToEventTarget, FromEventTarget
from .firestore_object import FirestoreObject


class RideRequest(FirestoreObject):
    """ Description
        This class represents a RideRequest object
    
    """

    @staticmethod
    def from_dict_and_reference(ride_request_dict, ride_request_ref):
        ride_request = RideRequest.from_dict(ride_request_dict)
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
        pickup_address = d['pickupAddress']
        has_checked_in = d['hasCheckedIn']
        event_ref = d['eventRef']  # TODO conversion to DocumentReference
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

            return AirportRideRequest(driver_status, pickup_address, has_checked_in,
                                      event_ref, orbit_ref, user_id, target, pricing, request_completion, flight_local_time,
                                      flight_number, airport_location, baggages, disabilities)
        elif ride_request_type == 'eventRide':
            # TODO change function calls
            return SocialEventRideRequest(driver_status, pickup_address, has_checked_in, event_ref, orbit_ref, user_id, target,
                                          pricing, request_completion)
        else:
            raise Exception(
                'Not supported rideRequestType: {}'.format(ride_request_type))

    def to_dict(self):
        ride_request_dict = {
            'driverStatus': self.driver_status,
            'pickupAddress': self.pickup_address,
            'hasCheckedIn': self.has_checked_in,
            'eventRef': self.event_ref,
            'orbitRef': self.orbit_ref,
            'userId': self.user_id,
            'target': self.target.to_dict(),
            'pricing': self.pricing,
            'requestCompletion': self.request_completion
        }
        return ride_request_dict

    def __init__(self, driver_status, pickup_address, has_checked_in, event_ref, orbit_ref, user_id, target, pricing,
                 request_completion):
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

        self.driver_status = driver_status
        self.pickup_address = pickup_address
        self.has_checked_in = has_checked_in
        self.event_ref = event_ref
        self.orbit_ref = orbit_ref
        self.user_id = user_id
        self.target = target
        self.pricing = pricing
        self.request_completion = request_completion


# class RideRequestActiveRecord(RideRequest):

#     @staticmethod
#     def fromFirestoreRef(firestoreRef, rideRequestDAO: RideRequestGenericDao, transaction: Transaction = None):
#         if (transaction):
#             return rideRequestDAO.getRideRequestWithTransaction(transaction, firestoreRef)
#         else:
#             return rideRequestDAO.getRideRequest(firestoreRef)

#     @staticmethod
#     def createFromDict(rideRequestDict, rideRequestGenericDao = RideRequestGenericDao()):
#         rideRequest = RideRequest.from_dict(rideRequestDict)
#         timestamp, documentRef = rideRequestGenericDao.createRideRequest()
#         rideRequest.set_firestore_ref(documentRef)
#         return rideRequest

#     def saveWithTransaction(self, transaction: Transaction):
#         # Save to database with ref specified instance variable
#         if (not self.__firestoreRef):
#             raise Exception('self.__firestoreRef not defined!')
#         RideRequestGenericDao.setRideRequestWithTransaction(transaction, self, self.__firestoreRef)


class AirportRideRequest(RideRequest):

    # TODO more arguments
    def __init__(self, driver_status, pickup_address, has_checked_in, event_ref, orbit_ref, user_id, target, pricing,
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

        super().__init__(driver_status, pickup_address,
                         has_checked_in, event_ref, orbit_ref, user_id, target, pricing, request_completion)
        self.rideCategory = 'airportRide'
        self.flightLocalTime = flight_local_time
        self.flightNumber = flight_number
        self.airportLocation = airport_location
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
        ride_request_dict['flightLocalTime'] = self.flightLocalTime
        ride_request_dict['flightNumber'] = self.flightNumber
        ride_request_dict['airportLocation'] = self.airportLocation
        ride_request_dict['baggages'] = self.baggages
        ride_request_dict['disabilities'] = self.disabilities
        return ride_request_dict


class SocialEventRideRequest(RideRequest):

    # TODO more arguments
    def __init__(self, driver_status, pickup_address, has_checked_in, event_ref, orbit_ref, user_id, target, pricing,
                 request_completion):
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

        super().__init__(driver_status, pickup_address,
                         has_checked_in, event_ref, orbit_ref, user_id, target, pricing, request_completion)
        self.rideCategory = 'eventRide'

    def to_dict(self):
        ride_request_dict = super().to_dict()
        ride_request_dict['rideCategory'] = 'eventRide'
        return ride_request_dict
