from typing import Type

class Target(object):

    def __init__(self, eventCategory, toEvent):
        self.eventCategory = eventCategory
        self.toEvent = toEvent

    @staticmethod
    def createTarget(targetDict: dict):
        toEvent = targetDict['toEvent']
        if (toEvent):
            return ToEventTarget(targetDict['eventCategory'], True, targetDict['arriveAtEventTime'])
        else: 
            return FromEventTarget(targetDict['eventCategory'], False, targetDict['leaveEventTime'])

class ToEventTarget(Target):

    def __init__(self, eventCategory, toEvent, arriveAtEventTime):
        super().__init__(eventCategory, toEvent)
        self.arriveAtEventTime = arriveAtEventTime

class FromEventTarget(Target):

    def __init__(self, eventCategory, toEvent, leaveEventTime):
        super().__init__(eventCategory, toEvent)
        self.leaveEventTime = leaveEventTime