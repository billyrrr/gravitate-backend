import datetime

import pytz
from iso8601 import iso8601


def local_time_from_timestamp(timestamp) -> str:
    """

    :param timestamp: for example: 1545062400
    :return: for example: "2018-12-17T08:00:00"
    """

    tz = pytz.timezone('US/Pacific') #('America/Los_Angeles')

    d: datetime.datetime = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    d = d.replace(tzinfo=None) # Convert to local time
    return d.isoformat()


def str_to_local_time(s) -> datetime.datetime:
    tz = pytz.timezone('America/Los_Angeles')
    return tz.localize(iso8601.parse_date(s, default_timezone=None))
