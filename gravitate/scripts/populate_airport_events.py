from gravitate.models import Event
from gravitate.data_access import EventDao, LocationGenericDao
import datetime
import pytz
import iso8601
import warnings

class EventBuilder(Event):
    """
    This class builds an event.

    """

    def __init__(self):
        """
        This method should class the following operations in the order of:
            1. buildBasicInfo
            2. buildLists
            3. buildTimeRange
            4. buildExtraInfo
        """
        self.buildBasicInfo()
        self.buildLists()
        self.buildTimeRange()
        self.buildExtraInfo()

    def buildBasicInfo(self):
        """
        This method fills basic information that is specified by subclass of EventBuilder.
        :return:
        """
        raise NotImplementedError

    def buildLists(self):
        """
        This method builds an empty list of participants.
        :return:
        """
        # Since we are unsure of how participants and locationRefs will be represented
        raise NotImplementedError

    def buildTimeRange(self):
        """
        This method builds the time range of the event
        :return:
        """
        raise NotImplementedError

    def buildExtraInfo(self):
        """
        This method builds extra information of the event such as pricing.
        :return:
        """
        raise NotImplementedError

class SpecifiedRangeEventBuilder(EventBuilder):

    def __init__(self, startTimestamp, endTimestamp):
        self.buildBasicInfo()
        self.buildLists()
        self.buildTimeRange(startTimestamp, endTimestamp)
        self.buildExtraInfo()

    def buildTimeRange(self, startTimestamp, endTimestamp):
        self.startTimestamp = startTimestamp
        self.endTimestamp = endTimestamp

class LaxEventBuilder(SpecifiedRangeEventBuilder):

    def buildBasicInfo(self):
        self.eventCategory = "airport"
        self.eventLocation = "LAX"
        self.isClosed = False
        self.locationRef = LocationGenericDao().findByAirportCode('LAX').getFirestoreRef()

    def buildLists(self):
        self.participants = []

    def buildExtraInfo(self):
        self.pricing = 100


class UcsbEventBuilder(SpecifiedRangeEventBuilder):

    def buildBasicInfo(self):
        self.eventCategory = "campus"
        self.eventLocation = "UCSB"
        self.isClosed = False
        self.locationRef = LocationGenericDao().findByCampusCode("UCSB").getFirestoreRef()

    def buildLists(self):
        self.participants = []

    def buildExtraInfo(self):
        self.pricing = 100


class SampleLaxEventBuilder(LaxEventBuilder):

    def buildTimeRange(self):
        self.startTimestamp = 1545033600
        self.endTimestamp = 1545119999


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
        newEvent = LaxEventBuilder(startTimestamp, endTimestamp)
        eventList.append(newEvent)

    return eventList


def populateEvents(startString="2018-12-07T08:00:00.000", numDays=35):
    startDatetime = generateStartDatetime(startString)
    timestampTupleList = generateTimestamps(startDatetime, numDays)
    eventList = generateEvents(timestampTupleList)
    for event in eventList:
        eventRef = EventDao().create(event)
        print(eventRef)
