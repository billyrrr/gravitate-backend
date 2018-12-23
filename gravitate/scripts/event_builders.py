from gravitate.data_access import LocationGenericDao
from gravitate.models import Event


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
        self.locationRef = LocationGenericDao().find_by_airport_code('LAX').get_firestore_ref()

    def buildLists(self):
        self.participants = []

    def buildExtraInfo(self):
        self.pricing = 100


class UcsbEventBuilder(SpecifiedRangeEventBuilder):

    def buildBasicInfo(self):
        self.eventCategory = "campus"
        self.eventLocation = "UCSB"
        self.isClosed = False
        self.locationRef = LocationGenericDao().find_by_campus_code("UCSB").get_firestore_ref()

    def buildLists(self):
        self.participants = []

    def buildExtraInfo(self):
        self.pricing = 100


class SampleLaxEventBuilder(LaxEventBuilder):

    def buildTimeRange(self):
        self.startTimestamp = 1545033600
        self.endTimestamp = 1545119999