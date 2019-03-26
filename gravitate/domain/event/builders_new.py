import datetime as dt
from typing import Type

import iso8601

from gravitate.data_access import LocationGenericDao
from gravitate.domain.event.models import Event
from gravitate.models import SocialEventLocation
from gravitate.models import ToEventTarget, FromEventTarget


def create_time_offsets(local_time, later=False, offset_low_abs_sec: int = 7200,
                                         offset_high_abs_sec: int = 18000):
    """
        This method creates a target with event start_time from Facebook dict.
            The offsets represents how much in advance is user's preferred earliest and latest.

        Limitations:
            this method won't work if any datetime string represents a time when
                daylight saving ends (November 4 1:00AM-2:00AM).
                since anytime in between corresponds to more than one possible UTC time.

    :param local_time:
    :param offset_low_abs_sec: The offset with lower absolute value.
    :param offset_high_abs_sec: The offset with higher absolute value.
    :return:
    """
    assert offset_low_abs_sec >= 0
    assert offset_high_abs_sec >= 0
    # Check that offsetLow represents a greater than or equal to interval than offsetHigh
    assert offset_low_abs_sec <= offset_high_abs_sec
    # Check that there earliest and latest represents a range of time
    assert offset_low_abs_sec != offset_high_abs_sec

    # tz = pytz.timezone('America/Los_Angeles')
    # local_time = tz.localize(iso8601.parse_date(flight_local_time))

    earliest: dt.datetime = None
    latest: dt.datetime = None

    # Get earliest and latest datetime
    if later:
        # Get timedelta object with seconds
        offset_earlier_abs = dt.timedelta(seconds=offset_low_abs_sec)
        offset_later_abs = dt.timedelta(seconds=offset_high_abs_sec)
        earliest = local_time + offset_earlier_abs
        latest = local_time + offset_later_abs
    else:
        # Get timedelta object with seconds
        offset_earlier_abs = dt.timedelta(seconds=offset_high_abs_sec)
        offset_later_abs = dt.timedelta(seconds=offset_low_abs_sec)
        earliest = local_time - offset_earlier_abs
        latest = local_time - offset_later_abs

    earliest_timestamp = int(earliest.timestamp())
    latest_timestamp = int(latest.timestamp())

    assert earliest_timestamp <= latest_timestamp  # Check that "earliest" occurs earlier than "latest"
    assert earliest_timestamp != latest_timestamp  # Check that "earliest" is not the same as latest

    return earliest_timestamp, latest_timestamp


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

    def build_descriptions(self, description, name):
        self._event_dict["description"] = description
        self._event_dict["name"] = name

    def _build_parking(self, parking_info=None, empty=False):
        if empty and parking_info is None:
            self._event_dict["parkingInfo"] = {
                "parkingAvailable": False,
                "parkingPrice": 0,
                "parkingLocation": "none"
            }
        else:
            self._event_dict["parkingInfo"] = parking_info


class FbEventBuilder(EventBaseBuilder):

    event_category = "social"

    def _build_basic_info(self):
        self._event_dict["eventCategory"] = self.event_category
        self._event_dict["isClosed"] = False
        self._event_dict["participants"] = []
        self._event_dict["pricing"] = 123456789
        # self._event_dict["parkingInfo"] = None

    def build_with_fb_dict(self, d: dict):
        """
        Builds SocialEvent with Facebook event json.

        TODO: finish
        {
            "description": "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com",
            "end_time": "2019-04-14T23:59:00-0700",
            "name": "Coachella Valley Music and Arts Festival 2019 - Weekend 1",
            "place": {
                "name": "Coachella",
                "location": {
                    "latitude": 33.679974,
                    "longitude": -116.237221
                },
                "id": "20281766647"
            },
            "start_time": "2019-04-12T12:00:00-0700",
            "id": "137943263736990"
        }

        :param d:
        :return:
        """
        self.build_descriptions(description=d["description"], name=d["name"])
        self._build_location(d["place"])
        self._build_basic_info()
        self._build_parking()
        self._build_fb_event_id(d)
        if "start_time" in d:
            self._build_start_time(d)
        if "end_time" in d:
            self._build_end_time(d)

    def _build_location(self, d):
        """
        Create location with facebook event - place
        :param d:
        :return:
        """
        location: SocialEventLocation = SocialEventLocation.from_fb_place(d)
        self._event_dict["locationRef"] = LocationGenericDao().insert_new(location)

    def _build_fb_event_id(self, d):
        """ Set self._event_dict["fbEventId"] with d["id]
            Note that type of id is str

        :param d:
        :return:
        """
        self._event_dict["fbEventId"] = d["id"]

    def _build_start_time(self, d):
        # raise NotImplementedError
        start_time_str = d["start_time"]
        start_time = iso8601.iso8601.parse_date(start_time_str)
        start_timestamp, end_timestamp = create_time_offsets(start_time, later=False)
        self._build_target(to_event=True, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
        self._event_dict["localDateString"] = start_time.strftime("%Y-%m-%d")

    def _build_end_time(self, d):
        end_time_str = d["end_time"]
        end_time = iso8601.iso8601.parse_date(end_time_str)
        start_timestamp, end_timestamp = create_time_offsets(end_time, later=True)
        self._build_target(to_event=False, start_timestamp=start_timestamp, end_timestamp=end_timestamp)


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


class CampusEventBuilder(EventBaseBuilder):

    event_category = "campus"

    def build_basic_info(self):
        self._event_dict["eventCategory"] = self.event_category
        self._event_dict["isClosed"] = False
        self._event_dict["participants"] = []
        self._event_dict["pricing"] = 123456789

    def build_campus(self, campus_code):
        self._event_dict["campusCode"] = campus_code
        self._event_dict["locationRef"] = LocationGenericDao().find_by_campus_code(campus_code).get_firestore_ref()

    def build_start_end(self, start_timestamp=None, end_timestamp=None, local_date_string=None):
        """ Build event start time and event end time
            Note that to-event and from-event targets are overlapping
        :param start_timestamp:
        :param end_timestamp:
        :return:
        """
        assert local_date_string is not None
        self._event_dict["localDateString"] = local_date_string

        if start_timestamp is not None:
            earliest_arrival = start_timestamp
            latest_arrival = start_timestamp + get_day_offset()
            self._build_target(to_event=True,
                               start_timestamp=earliest_arrival, end_timestamp=latest_arrival)

        if end_timestamp is not None:
            earliest_departure = start_timestamp
            latest_departure = start_timestamp + get_day_offset()
            self._build_target(to_event=False,
                               start_timestamp=earliest_departure, end_timestamp=latest_departure)


def build_ucsb_event(start_timestamp=None, end_timestamp=None, local_date_string=None):

    b = CampusEventBuilder()
    b.build_basic_info()
    b.build_campus(campus_code="UCSB")
    b.build_start_end(start_timestamp=int(start_timestamp), end_timestamp=int(end_timestamp),
                      local_date_string=local_date_string)
    b._build_parking(empty=True)
    campus_description = "UCSB on " + local_date_string
    b.build_descriptions(description=campus_description, name="UCSB")
    return b.export_as_class(Event)


def get_day_offset():
    """ Returns the offset of one day minus one second

    :return:
    """
    return 24 * 60 * 60 - 1

#
# class EventBuilder(Event):
#     """
#     This class builds an event.
#
#     """
#
#     def __init__(self):
#         """
#         This method should class the following operations in the order of:
#             1. buildBasicInfo
#             2. buildLists
#             3. buildTimeRange
#             4. buildExtraInfo
#         """
#         self.buildBasicInfo()
#         self.buildLists()
#         self.buildTimeRange()
#         self.buildExtraInfo()
#
#     def buildBasicInfo(self):
#         """
#         This method fills basic information that is specified by subclass of EventBuilder.
#         :return:
#         """
#         raise NotImplementedError
#
#     def buildLists(self):
#         """
#         This method builds an empty list of participants.
#         :return:
#         """
#         # Since we are unsure of how participants and locationRefs will be represented
#         raise NotImplementedError
#
#     def buildTimeRange(self, start_timestamp, end_timestamp):
#         """
#         This method builds the time range of the event
#         :return:
#         """
#         raise NotImplementedError
#
#     def buildExtraInfo(self):
#         """
#         This method builds extra information of the event such as pricing.
#         :return:
#         """
#         raise NotImplementedError
#
#
# class SpecifiedRangeEventBuilder(EventBuilder):
#
#     def __init__(self, start_timestamp, end_timestamp):
#         self.buildBasicInfo()
#         self.buildLists()
#         self.buildTimeRange(start_timestamp, end_timestamp)
#         self.buildExtraInfo()
#
#     def buildTimeRange(self, start_timestamp, end_timestamp):
#         self.start_timestamp = start_timestamp
#         self.end_timestamp = end_timestamp
#
# class LaxEventBuilder(SpecifiedRangeEventBuilder):
#
#     def buildBasicInfo(self):
#         self.event_category = "airport"
#         self.event_location = "LAX"
#         self.is_closed = False
#         self.location_ref = LocationGenericDao().find_by_airport_code('LAX').get_firestore_ref()
#
#     def buildLists(self):
#         self.participants = []
#
#     def buildExtraInfo(self):
#         self.pricing = 100
#
#
# class UcsbEventBuilder(SpecifiedRangeEventBuilder):
#
#     def buildBasicInfo(self):
#         self.event_category = "campus"
#         self.event_location = "UCSB"
#         self.is_closed = False
#         self.location_ref = LocationGenericDao().find_by_campus_code("UCSB").get_firestore_ref()
#
#     def buildLists(self):
#         self.participants = []
#
#     def buildExtraInfo(self):
#         self.pricing = 100
#
#
# class SampleLaxEventBuilder(LaxEventBuilder):
#
#     def buildTimeRange(self, start_timestamp=1545033600, end_timestamp=1545119999):
#         self.start_timestamp = start_timestamp
#         self.end_timestamp = end_timestamp
