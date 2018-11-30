from models.event import Event
from data_access.event_dao import EventDao
import datetime
import pytz
import iso8601
import warnings


class EventBuilder(Event):

    def __init__(self):
        self.buildBasicInfo()
        self.buildLists()
        self.buildTimeRange()
        self.buildExtraInfo()

    def buildBasicInfo(self):
        raise NotImplementedError

    def buildLists(self):
        # Since we are unsure of how participants and locationRefs will be represented
        raise NotImplementedError

    def buildTimeRange(self):
        raise NotImplementedError

    def buildExtraInfo(self):
        raise NotImplementedError


class LaxEventBuilder(EventBuilder):

    def buildBasicInfo(self):
        self.eventCategory = "airport"
        self.eventLocation = "LAX"

    def buildLists(self):
        self.participants = []
        self.locationRefs = []

    def buildExtraInfo(self):
        self.pricing = 100


class SampleLaxEventBuilder(LaxEventBuilder):

    def buildTimeRange(self):
        self.startTimestamp = 1545033600
        self.endTimestamp = 1545119999


class SpecifiedRangeLaxEventBuild(LaxEventBuilder):

    def __init__(self, startTimestamp, endTimestamp):
        self.buildBasicInfo()
        self.buildLists()
        self.buildTimeRange(startTimestamp, endTimestamp)
        self.buildExtraInfo()

    def buildTimeRange(self, startTimestamp, endTimestamp):
        self.startTimestamp = startTimestamp
        self.endTimestamp = endTimestamp


def generateStartDatetime(startDayDatetimeStr: str) -> datetime.datetime:
    """ Description
    :type startDayDatetimeStr:str:
    :param startDayDatetimeStr:str: ie. "2018-12-17T08:00:00.000"

    :raises:

    :rtype:
    """
    tz = pytz.timezone('America/Los_Angeles')

    startDayDatetime = iso8601.parse_date(
        startDayDatetimeStr, default_timezone=None).astimezone(tz)

    # Represents "2018-12-17T00:00:00.000" 'America/Los_Angeles'
    startDatetime: datetime.datetime = datetime.datetime(
        startDayDatetime.year, startDayDatetime.month, startDayDatetime.day, tzinfo=None).astimezone(tz)

    return startDatetime


def generateTimestamps(startDatetime: datetime.datetime, numDays: int) -> [(int, int)]:

    curStart = startDatetime
    curNumDays = 0
    tupleList = list()

    while (curNumDays < numDays):
        endDatetime = curStart + \
            datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

        # Handles the case where 1 day after startDatetime and 1 second before is still tomorrow
        # (which is not expected to occur in California)
        while (endDatetime.day != curStart.day):
            warnings.warn(
                "1 day after startDatetime and 1 second before is still tomorrow. curStart = {}".format(curStart))
            assert startDatetime.timestamp() < endDatetime.timestamp()
            endDatetime = endDatetime - datetime.timedelta(seconds=1)

        startTimestamp = int(curStart.timestamp())
        endTimestamp = int(endDatetime.timestamp())
        tupleList.append((startTimestamp, endTimestamp))

        # Increase counter and curStart
        curNumDays += 1
        curStart = curStart + datetime.timedelta(days=1)

    return tupleList


def generateEvents(timestampTupleList: list):

    eventList = list()

    for startTimestamp, endTimestamp in timestampTupleList:
        newEvent = SpecifiedRangeLaxEventBuild(startTimestamp, endTimestamp)
        eventList.append(newEvent)

    return eventList


def populateEvents(startString="2018-12-07T08:00:00.000", numDays=35):
    startDatetime = generateStartDatetime(startString)
    timestampTupleList = generateTimestamps(startDatetime, numDays)
    eventList = generateEvents(timestampTupleList)
    for event in eventList:
        eventRef = EventDao().create(event)
        print(eventRef)
