import datetime
from math import inf

import pytz
from iso8601 import iso8601

import random
import string


def random_id():
    """
        Generate a random string with 32 characters.
        https://www.geeksforgeeks.org/generating-random-ids-python/
    """
    randomIdStr = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    return randomIdStr


def local_dt_from_timestamp(timestamp) -> datetime.datetime:
    """

    :param timestamp: for example: 1545062400
    :return: datetime
    """
    tz = pytz.timezone('US/Pacific') #('America/Los_Angeles')

    d: datetime.datetime = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    d = d.replace(tzinfo=None) # Convert to local time

    return d


def local_time_from_timestamp(timestamp) -> str:
    """

    :param timestamp: for example: 1545062400
    :return: for example: "2018-12-17T08:00:00"
    """
    d = local_dt_from_timestamp(timestamp)
    return d.isoformat()


def str_to_local_time(s) -> datetime.datetime:
    tz = pytz.timezone('America/Los_Angeles')
    return tz.localize(iso8601.parse_date(s, default_timezone=None))


def timestamp_from_local_time(s) -> int:
    return int(str_to_local_time(s).timestamp())
