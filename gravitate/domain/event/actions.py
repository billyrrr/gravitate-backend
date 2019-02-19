from . import builders


def create(args, user_id, event_category="social"):

    if event_category == "social":
        return _create_social_event(args, user_id)
    else:
        raise ValueError("event_category not supported: {}".format(event_category))


def _create_social_event(args, user_id):
    """
    TODO: implement
    :param args:
    :param user_id:
    :return:
    """
    raise NotImplementedError
