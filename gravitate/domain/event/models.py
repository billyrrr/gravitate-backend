"""
Author: Andrew Kim
Reviewer: Zixuan Rao
"""

from gravitate.models import Target
from gravitate.models.firestore_object import FirestoreObject


# event class
class Event(FirestoreObject):
    """ Description
    this class represents the event object
        Note that reference to the object eventRef is deprecated.
        Get and set firestoreRef instead.

    """

    @staticmethod
    def from_dict_and_reference(eventDict, eventRef):
        event = Event.from_dict(eventDict)
        event.set_firestore_ref(eventRef)
        return event

    @staticmethod
    def from_dict(eventDict):
        """ Description
            This function creates an event

            :param eventDict:
        """
        event_category = eventDict['eventCategory']
        participants = eventDict['participants']
        # event_location = eventDict['eventLocation']
        # start_timestamp = eventDict['startTimestamp']
        # end_timestamp = eventDict['endTimestamp']
        targets = eventDict['targets']
        pricing = eventDict['pricing']
        location_ref = eventDict['locationRef']
        is_closed = eventDict['isClosed']
        local_date_string = eventDict['localDateString']
        name = eventDict['name']
        description = eventDict['description']
        parking_info = eventDict['parkingInfo']
        if event_category == "airport":
            airport_code = eventDict['airportCode']
            return AirportEvent(event_category, participants, targets, pricing, location_ref,
                         is_closed, local_date_string, name, description, parking_info, airport_code)
        elif event_category == "social":
            fb_event_id = eventDict["fbEventId"]
            return SocialEvent(event_category, participants, targets, pricing, location_ref,
                 is_closed, local_date_string, name, description, parking_info, fb_event_id)
        elif event_category == "campus":
            campus_code = eventDict["campusCode"]
            return CampusEvent(event_category, participants, targets, pricing, location_ref,
                               is_closed, local_date_string, name, description, parking_info, campus_code)
        else:
            raise NotImplementedError

    def to_dict(self):
        eventDict = {
            'eventCategory': self.event_category,
            'participants': self.participants,
            # 'eventLocation': self.event_location,
            # 'startTimestamp': self.start_timestamp,
            # 'endTimestamp': self.end_timestamp,
            'targets': [ target.to_dict() for target in self.targets],
            'pricing': self.pricing,
            'locationRef': self.location_ref,
            'isClosed': self.is_closed,
            'localDateString': self.local_date_string,
            'name': self.name,
            'description': self.description,
            'parkingInfo': self.parking_info
        }
        return eventDict

    def to_dict_view(self):
        dict_view = {
            'eventCategory': self.event_category,
            'participants': self.participants,
            'pricing': self.pricing,
            'locationId': self.location_ref.id,
            'isClosed': self.is_closed,
            'localDateString': self.local_date_string,  # Start date
            'name': self.name,
            'description': self.description,
            'parkingInfo': self.parking_info
        }
        for target in self.targets:
            # Note that latest arrival means the latest time to arrive at the event
            #       and earliest departure is the earliest time to leave an event
            if target.to_event:
                dict_view['earliestArrival'] = target.get_earliest_arrival_view()
                dict_view['latestArrival'] = target.get_latest_arrival_view()
            else:
                dict_view['earliestDeparture'] = target.get_earliest_departure_view()
                dict_view['latestDeparture'] = target.get_latest_departure_view()
        return dict_view

    def set_as_active(self):
        """ Definition
            Sets the boolean isClosed to False

            :param self:
        """
        self.is_closed = False

    def set_as_passed(self):
        """ Definition
            Sets the boolean isClosed to True

            :param self:
        """
        self.is_closed = True

    def __init__(self, event_category, participants, targets, pricing, location_ref,
                 is_closed, local_date_string, name, description, parking_info):
        """Description
           This function initializes an Event object

           :param self:
           :param event_category:
           :param participants:
           :param start_timestamp:
           :param end_timestamp:
           :param pricing:
           :param location_ref: a list of locationRef that corresponds to this event
           :param is_closed:
        """
        self.event_category = event_category
        self.participants = participants
        self.targets = list()
        for target_dict in targets:
            target = Target.from_dict(target_dict)
            self.targets.append(target)
        self.pricing = pricing
        self.location_ref = location_ref
        self.is_closed = is_closed
        self.local_date_string = local_date_string
        self.name = name
        self.description = description
        self.parking_info = parking_info


class AirportEvent(Event):

    @staticmethod
    def from_dict_and_reference(eventDict, eventRef):
        raise NotImplementedError

    # @staticmethod
    # def from_dict(eventDict):
    #     event_category = eventDict['eventCategory']
    #     participants = eventDict['participants']
    #     # event_location = eventDict['eventLocation']
    #     # start_timestamp = eventDict['startTimestamp']
    #     # end_timestamp = eventDict['endTimestamp']
    #     targets = eventDict['targets']
    #     pricing = eventDict['pricing']
    #     location_ref = eventDict['locationRef']
    #     is_closed = eventDict['isClosed']
    #     local_date_string = eventDict['localDateString']
    #     name = eventDict['name']
    #     description = eventDict['description']
    #     airport_code = eventDict['airportCode']
    #     parking_info = eventDict['parkingInfo']
    #
    #     return AirportEvent(event_category, participants, targets, pricing, location_ref,
    #                  is_closed, local_date_string, name, description, parking_info, airport_code)

    def __init__(self, event_category, participants, targets, pricing, location_ref,
                 is_closed, local_date_string, name, description, parking_info, airport_code):
        super().__init__(event_category, participants, targets, pricing, location_ref,
                 is_closed, local_date_string, name, description, parking_info)
        self.airport_code = airport_code

    def to_dict(self):
        eventDict = super().to_dict()
        eventDict['airportCode'] = self.airport_code
        return eventDict

    def to_dict_view(self):
        dict_view = super().to_dict_view()
        dict_view["airportCode"] = self.airport_code
        return dict_view


class SocialEvent(Event):
    """ Description
        this class represents the event object
            Note that reference to the object eventRef is deprecated.
            Get and set firestoreRef instead.

        """

    @staticmethod
    def from_dict_and_reference(eventDict, eventRef):
        event = Event.from_dict(eventDict)
        event.set_firestore_ref(eventRef)
        return event

    def to_dict(self):
        eventDict = super().to_dict()
        eventDict['fbEventId'] = self.fb_event_id
        return eventDict

    def set_as_active(self):
        """ Definition
            Sets the boolean isClosed to False

            :param self:
        """
        self.is_closed = False

    def set_as_passed(self):
        """ Definition
            Sets the boolean isClosed to True

            :param self:
        """
        self.is_closed = True

    def __init__(self, event_category, participants, targets, pricing, location_ref,
                 is_closed, local_date_string, name, description, parking_info, fb_event_id):
        super().__init__(event_category, participants, targets, pricing, location_ref,
                 is_closed, local_date_string, name, description, parking_info)
        self.fb_event_id = fb_event_id

    def to_dict_view(self):
        # for target in self.targets:
        d_view = super().to_dict_view()
        d_view["fbEventId"] = self.fb_event_id
        return d_view


class CampusEvent(Event):

    @staticmethod
    def from_dict_and_reference(eventDict, eventRef):
        event = Event.from_dict(eventDict)
        event.set_firestore_ref(eventRef)
        return event

    def to_dict(self):
        eventDict = super().to_dict()
        eventDict['campusCode'] = self.campus_code
        return eventDict

    def set_as_active(self):
        """ Definition
            Sets the boolean isClosed to False

            :param self:
        """
        self.is_closed = False

    def set_as_passed(self):
        """ Definition
            Sets the boolean isClosed to True

            :param self:
        """
        self.is_closed = True

    def __init__(self, event_category, participants, targets, pricing, location_ref,
                 is_closed, local_date_string, name, description, parking_info, campus_code):
        super().__init__(event_category, participants, targets, pricing, location_ref,
                         is_closed, local_date_string, name, description, parking_info)
        self.campus_code = campus_code

    def to_dict_view(self):
        # for target in self.targets:
        d_view = super().to_dict_view()
        d_view["campusCode"] = self.campus_code
        return d_view

