import datetime
import warnings

import iso8601
import pytz


def generateStartDatetime(startDayDatetimeStr: str) -> datetime.datetime:
    """ Description
    :type startDayDatetimeStr:str:
    :param startDayDatetimeStr:str: ie. "2018-12-17T08:00:00.000"

    :raises:

    :rtype:
    """
    tz = pytz.timezone('US/Pacific') #('America/Los_Angeles')

    startDayDatetime = iso8601.parse_date(
        startDayDatetimeStr, default_timezone=None) #.astimezone(tz)

    # Represents "2018-12-17T00:00:00.000" 'America/Los_Angeles'
    # Note that this line of code is not correct and works by magic
    startDatetimeLocal: datetime.datetime = datetime.datetime(
        startDayDatetime.year, startDayDatetime.month, startDayDatetime.day, tzinfo=None)
    # print(str(startDatetimeLocal.day) + "  " + str(startDatetimeLocal.hour))
    startDatetime = tz.localize(startDatetimeLocal) #.astimezone(tz=tz)

    return startDatetime


def generateTimestamps(startDatetime: datetime.datetime, numDays: int) -> [(int, int)]:
    curStart = startDatetime
    curNumDays = 0
    tupleList = list()

    while curNumDays < numDays:
        endDatetime = curStart + \
                      datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

        # Handles the case where 1 day after startDatetime and 1 second before is still tomorrow
        # (which is not expected to occur in California)
        while endDatetime.day != curStart.day:
            warnings.warn(
                "1 day after startDatetime and 1 second before is not today. curStart = {}".format(curStart))
            assert startDatetime.timestamp() < endDatetime.timestamp()
            endDatetime = endDatetime - datetime.timedelta(seconds=1)

        startTimestamp = int(curStart.timestamp())
        endTimestamp = int(endDatetime.timestamp())
        dateString = curStart.strftime("%Y-%m-%d")
        tupleList.append((startTimestamp, endTimestamp, dateString, ))

        # Increase counter and curStart
        curNumDays += 1
        curStart = curStart + datetime.timedelta(days=1)

    return tupleList
