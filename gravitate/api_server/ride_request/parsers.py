"""
Switch to reqparse to reduce repeated code for different types of rideRequest

"""

from flask_restful import reqparse

# Parse field values from json
ride_request_base_parser = reqparse.RequestParser(bundle_errors=True)
ride_request_base_parser.add_argument('pickupAddress', type=str, help='Pickup Address', location="json")
ride_request_base_parser.add_argument('toEvent', type=bool, help='whether the ride is heading to the event',
                                      location="json")
ride_request_base_parser.add_argument('driverStatus', type=bool,
                                      help="whether the user want to be considered as a driver for the event",
                                      location="json")

# Parse field values from json
airport_parser = ride_request_base_parser.copy()
airport_parser.add_argument('flightNumber', type=str, help='Flight Number', location="json")
airport_parser.add_argument('airportCode', type=str, help='Airport Code', location="json")
airport_parser.add_argument('flightLocalTime', type=str, help='Flight Local Time ISO8601', location="json")

# Parse field values from json
social_event_ride_parser = ride_request_base_parser.copy()
social_event_ride_parser.add_argument('eventId', type=str, help="Event ID", location="json")

"""
RideRequest creation useCase: FL-3: Connecting Flight Using Flight Number
"""
mockJson = {
    "Nothing": True  # TODO: move mock JSON to test/factory
}

luggage_parser = reqparse.RequestParser(bundle_errors=True)
luggage_parser.add_argument('luggages', type=list,
                            help="the list of luggages",
                            location="json")
