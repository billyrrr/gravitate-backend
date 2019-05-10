from gravitate.api_server.event import parsers as event_parser
from gravitate.domain.event import builders_new as event_builders, models as event_models
from gravitate.domain.event.dao import EventDao
from gravitate.domain.user import UserDao


def create(args, user_id, event_category="social"):
    """ Creates event in the database.

    :param args:
    :param user_id:
    :param event_category:
    :return:
    """
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


def create_fb_event(event_dict, uid):
    """ Creates event from a facebook event.

    :param event_dict: event json returned by Facebook graph api
    :param uid: user id
    :return: event id just created
    """
    b = event_builders.FbEventBuilder()
    # print(event_dict)
    b.build_with_fb_dict(event_dict)
    e: event_models.SocialEvent = b.export_as_class(event_models.SocialEvent)
    # Note that e.firestore_ref will not be set by create()
    ref = EventDao().create_fb_event(e)
    e.set_firestore_ref(ref)
    dict_view = e.to_dict_view()
    dict_view["eventId"] = ref.id
    # TODO: add error handling
    UserDao().add_user_event_dict(uid, dict_view["fbEventId"], dict_view)
    event_id = ref.id
    return event_id
