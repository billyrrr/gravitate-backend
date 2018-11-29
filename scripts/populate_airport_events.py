from models.event import Event

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



