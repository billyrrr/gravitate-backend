from gravitate.domain.event.builders import UcsbEventBuilder
from gravitate.domain.event.builders_new import AirportEventBuilder
from gravitate.domain.event.dao import EventDao
from gravitate.domain.event.models import AirportEvent
from gravitate.scripts.utils import generateStartDatetime, generateTimestamps


def generate_airport_events(timestamp_tuple_list: list):
    event_list = list()

    for startTimestamp, endTimestamp, dateStr in timestamp_tuple_list:
        # new_event = LaxEventBuilder(startTimestamp, endTimestamp)
        b = AirportEventBuilder()
        b = AirportEventBuilder()
        b.build_airport("LAX")
        b.build_basic_info()
        b._build_target(to_event=True, start_timestamp=startTimestamp, end_timestamp=endTimestamp)
        b._build_target(to_event=False, start_timestamp=startTimestamp, end_timestamp=endTimestamp)
        b.build_descriptions("what the event is", "name of the event")
        b.build_parking()
        b._build_local_date_string(dateStr)
        new_event = b.export_as_class(AirportEvent)
        event_list.append(new_event)

    return event_list


def generate_uc_events(timestamp_tuple_list: list):
    event_list = list()

    for startTimestamp, endTimestamp in timestamp_tuple_list:
        new_event = UcsbEventBuilder(startTimestamp, endTimestamp)
        event_list.append(new_event)

    return event_list


def populate_events(start_string="2018-12-07T08:00:00.000", num_days=35, event_category="airport"):
    start_datetime = generateStartDatetime(start_string)
    timestamp_tuple_list = generateTimestamps(start_datetime, num_days)
    assert event_category == "airport" or event_category == "campus"
    event_list = generate_airport_events(timestamp_tuple_list) if event_category == "airport" else generate_uc_events(
        timestamp_tuple_list)
    for event in event_list:
        event_ref = EventDao().create(event)
        print(event_ref)


class PopulateEventCommand:

    def __init__(self, start_string="2018-12-07T08:00:00.000", num_days=35, event_category="airport"):
        assert event_category == "airport" or event_category == "campus"
        self.start_string = start_string
        self.num_days = num_days
        self.event_category = event_category

    def execute(self) -> list:
        """

        :return: a list of DocumentReference for documents just created
        """

        refs = list()

        start_datetime = generateStartDatetime(self.start_string)
        timestamp_tuple_list = generateTimestamps(start_datetime, self.num_days)

        event_list = generate_airport_events(timestamp_tuple_list) \
            if self.event_category == "airport" \
            else generate_uc_events(timestamp_tuple_list)

        for event in event_list:
            event_ref = EventDao().create(event)
            refs.append(event_ref)
            print(event_ref)

        return refs
