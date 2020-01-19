"""
Author: Zixuan Rao
Reference: https://github.com/faif/python-patterns/blob/master/creational/builder.py

"""
from gravitate.domain.location import Location, AirportLocation


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
        return AirportLocation.from_dict(self.locationDict)


class LaxBuilder(LocationBuilder):
    """
    Description This class builds an LAX location
    
        Note that buildAirportInfo does not build airportLocation, the user is expected to provide that. 

        :param LocationBuilder: 
    """

    def buildAirportInfo(self):
        self.locationDict['airportCode'] = 'LAX'
        self.locationDict['obj_type'] = 'AirportLocation'

    def buildBasicInfo(self):
        self.locationDict['coordinates'] = {
            'latitude': 33.94211345,
            'longitude': -118.4070573902485
        }
        self.locationDict['address'] = '1 World Way, Los Angeles, CA 90045'


class SanBuilder(LocationBuilder):
    """ Description
    This class builds a SAN (San Diego International Airport) location.
    """

    def buildAirportInfo(self):
        self.locationDict['airportCode'] = 'SAN'
        self.locationDict['obj_type'] = 'AirportLocation'

    def buildBasicInfo(self):
        self.locationDict['coordinates'] = {
            'latitude': 32.733909,
            'longitude': -117.193304
        }
        self.locationDict['address'] = '3225 N Harbor Dr, San Diego, CA 92101'


def buildLaxTerminal(terminal: str):
    otherParams = {
        'terminal': terminal
    }
    terminal = LaxBuilder()
    terminal.mergeDict(otherParams)
    airportLocation = terminal.exportToLocation()
    return airportLocation


def doWorkUc(campusCode="UCSB"):
    campusLocation = Location.from_code("UCSB", "campus")
    campusLocation.save()
    ref = campusLocation.doc_ref
    campusLocation.set_firestore_ref(ref)


def doWorkDeprecated():
    terminals = ['1', '2', '3', '4', '5', '6', '7', '8', 'B']

    for terminal in terminals:
        airportLocation = buildLaxTerminal(terminal)
        airportLocation.save()
        ref = airportLocation.doc_ref
        airportLocation.set_firestore_ref(ref)
        print(vars(airportLocation))


def doWork(airportCode='LAX'):
    airportLocation = None

    if airportCode == 'LAX':
        airportLocation = LaxBuilder().exportToLocation()
        airportLocation.save()
    elif airportCode == 'SAN':
        airportLocation = SanBuilder().exportToLocation()
        airportLocation.save()
    else:
        raise ValueError

    print(vars(airportLocation))


class PopulateLocationCommand:

    def __init__(self, airport_code='LAX'):
        self.airport_code = airport_code

    def execute(self) -> list:
        """

        :return: a list of DocumentReference for all Documents created
        """

        airportLocation = None
        refs = list()

        if self.airport_code == 'LAX':
            airportLocation = LaxBuilder().exportToLocation()
            airportLocation.save()
            # ref = LocationGenericDao().insert_new(airportLocation)
            # airportLocation.set_firestore_ref(ref)
            refs.append(airportLocation.doc_ref)
        elif self.airport_code == 'SAN':
            airportLocation = SanBuilder().exportToLocation()
            # ref = LocationGenericDao().insert_new(airportLocation)
            # airportLocation.set_firestore_ref(ref)
            airportLocation.save()
            refs.append(airportLocation.doc_ref)
        else:
            raise ValueError("unsupported airportCode: {}".format(self.airport_code))

        print(vars(airportLocation))

        return refs
