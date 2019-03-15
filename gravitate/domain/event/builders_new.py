from typing import Type

from gravitate.data_access import LocationGenericDao
from gravitate.domain.event.models import Event
from gravitate.models import ToEventTarget, FromEventTarget


class EventBaseBuilder:

    event_category = None

    def __init__(self):
        self._event_dict = dict()

    def export_as_class(self, export_class) -> Type[Event]:
        return export_class.from_dict(self._event_dict)

    def _build_target(self, to_event, start_timestamp, end_timestamp):
        """
        Note that this is an abstract class.
            self.event_category needs to be defined in subclass.
        :param to_event:
        :param start_timestamp:
        :param end_timestamp:
        :return:
        """
        assert self.event_category is not None
        if "targets" not in self._event_dict.keys():
            self._event_dict["targets"] = list()
        if to_event:
            self._event_dict["targets"].append(
                ToEventTarget(event_category=self.event_category,
                              arrive_at_event_time={
                                  'earliest': start_timestamp,
                                  'latest': end_timestamp
                              }).to_dict()
            )
        else:
            self._event_dict["targets"].append(
                FromEventTarget(event_category=self.event_category,
                                leave_event_time={
                                    'earliest': start_timestamp,
                                    'latest': end_timestamp
                                }).to_dict()
            )

    def _build_local_date_string(self, local_date_string):
        self._event_dict["localDateString"] = local_date_string


class AirportEventBuilder(EventBaseBuilder):

    event_category = "airport"

    def build_basic_info(self):
        self._event_dict["eventCategory"] = self.event_category
        self._event_dict["isClosed"] = False
        self._event_dict["participants"] = []
        self._event_dict["pricing"] = 123456789

    def build_airport(self, airport_code):
        self._event_dict["airportCode"] = airport_code
        self._event_dict["locationRef"] = LocationGenericDao().find_by_airport_code(airport_code).get_firestore_ref()

    def build_parking(self, parking_info = None):
        if parking_info is None:
            self._event_dict["parkingInfo"] = {
                "parkingAvailable": False,
                "parkingPrice": 0,
                "parkingLocation": "none"
            }
        else:
            self._event_dict["parking_info"] = parking_info

    def build_descriptions(self, description, name):
        self._event_dict["description"] = description
        self._event_dict["name"] = name



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

    def buildTimeRange(self, start_timestamp, end_timestamp):
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

    def __init__(self, start_timestamp, end_timestamp):
        self.buildBasicInfo()
        self.buildLists()
        self.buildTimeRange(start_timestamp, end_timestamp)
        self.buildExtraInfo()

    def buildTimeRange(self, start_timestamp, end_timestamp):
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp

class LaxEventBuilder(SpecifiedRangeEventBuilder):

    def buildBasicInfo(self):
        self.event_category = "airport"
        self.event_location = "LAX"
        self.is_closed = False
        self.location_ref = LocationGenericDao().find_by_airport_code('LAX').get_firestore_ref()

    def buildLists(self):
        self.participants = []

    def buildExtraInfo(self):
        self.pricing = 100


class UcsbEventBuilder(SpecifiedRangeEventBuilder):

    def buildBasicInfo(self):
        self.event_category = "campus"
        self.event_location = "UCSB"
        self.is_closed = False
        self.location_ref = LocationGenericDao().find_by_campus_code("UCSB").get_firestore_ref()

    def buildLists(self):
        self.participants = []

    def buildExtraInfo(self):
        self.pricing = 100


class SampleLaxEventBuilder(LaxEventBuilder):

    def buildTimeRange(self, start_timestamp=1545033600, end_timestamp=1545119999):
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
