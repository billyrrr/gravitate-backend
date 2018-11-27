"""
Author: Zixuan Rao
Reference: https://github.com/faif/python-patterns/blob/master/creational/builder.py

"""
from models.location import Location, AirportLocation
from data_access.location_dao import LocationGenericDao

class LocationBuilder(object):

    def __init__(self):
        self.locationDict = dict()
        self.buildAirportInfo()
        self.buildBasicInfo()

    def buildAirportInfo(self):
        raise NotImplementedError
    
    def buildBasicInfo(self):
        raise NotImplementedError
    
    def mergeDict(self, otherDict: dict):
        self.locationDict.update(otherDict)

    def exportToLocation(self):
        return Location.fromDict(self.locationDict)

class LaxBuilder(LocationBuilder):
    """
    Description: This class builds an LAX location
    
        Note that buildAirportInfo does not build airportLocation, the user is expected to provide that. 

        :param LocationBuilder: 
    """
    def buildAirportInfo(self):
        self.locationDict['airportCode'] = 'LAX'
        self.locationDict['locationCategory'] = 'airport'
        
    def buildBasicInfo(self):
        self.locationDict['coordinates'] = {
            'latitude': 33.94211345,
            'longitude': -118.4070573902485
        }
        self.locationDict['address'] = '1 World Way, Los Angeles, CA 90045'


def buildLaxTerminal(terminal: str):
    otherParams = {
        'terminal': terminal
    }
    terminal = LaxBuilder()
    terminal.mergeDict(otherParams)
    airportLocation = terminal.exportToLocation()
    print(airportLocation.toDict())

buildLaxTerminal('1')    
