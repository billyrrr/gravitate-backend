"""
Switch to reqparse to reduce repeated code for different types of rideRequest

"""

from flask_restful import reqparse

# Parse field values from url path
airport_parser = reqparse.RequestParser(bundle_errors=True)
airport_parser.add_argument('flightNumber', type=str, help='Flight Number', location="json")
airport_parser.add_argument('airportCode', type=str, help='Airport Code', location="json")
airport_parser.add_argument('flightLocalTime', type=str, help='Flight Local Time ISO8601', location="json")
airport_parser.add_argument('pickupAddress', type=str, help='Pickup Address', location="json")
airport_parser.add_argument('toEvent', type=bool, help='whether the ride is heading to the event', location="json")
airport_parser.add_argument('driverStatus', type=bool,
                            help="whether the user want to be considered as a driver for the event", location="json")


"""
RideRequest creation useCase: FL-3: Connecting Flight Using Flight Number
"""
mockJson = {
    ""
}
