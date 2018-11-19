from typing import Type


class Target(object):

    def __init__(self, eventCategory):
        self.eventCategory = eventCategory

    @staticmethod
    def fromDict(targetDict: dict):
        toEvent = targetDict['toEvent']
        if (toEvent):
            return ToEventTarget(targetDict['eventCategory'], targetDict['arriveAtEventTime'])
        else:
            return FromEventTarget(targetDict['eventCategory'], targetDict['leaveEventTime'])

    @staticmethod
    def createAirportEventTarget(toEvent: bool, earliest:int, latest:int):
        if (toEvent):
            return ToEventTarget('airportRide', {
                'earliest': earliest,
                'latest': latest,
                # TODO add timezone
            })
        else:
            return FromEventTarget('airportRide', {
                'earliest': earliest,
                'latest': latest
            })

    def toDict(self):
        """ Description
            This function returns a dictionary of the target. 

        :type self:
        :param self:
    
        :raises:
    
        :rtype:
        """ 
        targetDict = {
            u'eventCategory': self.eventCategory
        }
        return targetDict


class ToEventTarget(Target):

    def __init__(self, eventCategory, arriveAtEventTime):
        super().__init__(eventCategory)
        self.arriveAtEventTime = arriveAtEventTime

    def toDict(self):
        targetDict = super().toDict()
        targetDict[u'toEvent'] = True
        targetDict[u'arriveAtEventTime'] = self.arriveAtEventTime
        return targetDict


class FromEventTarget(Target):

    def __init__(self, eventCategory, leaveEventTime):
        super().__init__(eventCategory)
        self.leaveEventTime = leaveEventTime

    def toDict(self):
        targetDict = super().toDict()
        targetDict[u'toEvent'] = False
        targetDict[u'leaveEventTime'] = self.leaveEventTime
        return targetDict
