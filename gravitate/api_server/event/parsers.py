"""
Switch to reqparse to reduce repeated code for different types of rideRequest

"""

from flask_restful import reqparse

# Parse field values from json
# TODO: add more arguments once event json is designed
event_parser = reqparse.RequestParser(bundle_errors=True)
event_parser.add_argument('eventLocation', type=str, help='venue of the event ', location="json")
event_parser.add_argument('locationId', type=str, help='location id associated with the event', location="json")

# Parser for social event
social_event_parser = event_parser.copy()
social_event_parser.add_argument('info', type=dict, help="relevant information (eg. parking information)", location="json",
                          required=False)

