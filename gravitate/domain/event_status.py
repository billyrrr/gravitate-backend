"""
Author: Andrew Kim
"""

import datetime

from gravitate.domain.event.models import Event


def refresh_event_status(event: Event):
    """ Definition
        Sets the event to a past event category one day after the start time
    """
    ts = datetime.datetime.now().timestamp()
    # check if refresh_event_status is True before proceeding
    if not event.is_closed and ts >= event.end_timestamp:
        return True
    else:
        return False


def close_event(event: Event):
    event.is_closed = True
