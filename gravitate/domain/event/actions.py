from . import builders
from flask_restful import reqparse
from gravitate.api_server.event import parsers as event_parser

def create(args, user_id, event_category="social"):

    if event_category == "social":
        return _create_social_event(args, user_id)
    else:
        raise ValueError("event_category not supported: {}".format(event_category))


def _create_social_event(event_dict: dict, user_id):
    """
    TODO: implement
    :param args:
    :param user_id:
    :return:
    """
    p = event_parser.social_event_parser.parse_args()
    event_dict = p.values()

