import datetime

import pytz


def local_time_from_timestamp(timestamp) -> str:
    """

    :param timestamp: for example: 1545062400
    :return: for example: "2018-12-17T08:00:00"
    """

    tz = pytz.timezone('US/Pacific') #('America/Los_Angeles')

    d: datetime.datetime = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    d = d.replace(tzinfo=None) # Convert to local time
    return d.isoformat()