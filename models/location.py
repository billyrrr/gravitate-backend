

class Location:

    coordinates = {
        'latitude': None,
        'longitude': None
    }

    def __init__(self, coordinates, address):
        self.coordinates = coordinates
        self.address = address

    @staticmethod
    def fromDict(locationDict):
        coordinates = locationDict['coordinates']
        address = locationDict['address']
        locationCategory = locationDict['locationCategory']
        if locationCategory == 'airport':
            terminal = locationDict['terminal']
            airportCode = locationDict['airportCode']
            return AirportLocation(coordinates, address, terminal, airportCode)
        elif locationCategory == 'event':
            # TODO generate event
            raise NotImplementedError(
                'Event location is not yet implemented. ')
        else:
            raise NotImplementedError(
                'Unsupported locationCategory ' + str(locationCategory) + '. ')
    
    def toDict(self) -> dict:
        return {
            'coordinates': self.coordinates,
            'address': self.address
        }


class AirportLocation(Location):
    """
    Description: 
        This class represennts an airport location. 
        Two airport locations are considered the same if 
            their airportCode (ie. "LAX") and terminal (ie. "1")
            are identical. 

        :param Location: 
    """

    def __init__(self, coordinate, address, terminal, airportCode):
        super(coordinate, address)
        self.locationCategory = 'airport'
        self.airportCode = airportCode
        self.terminal = terminal

    __firestoreRef = None

    def setFirestoreRef(self, firestoreRef: str):
        self.__firestoreRef = firestoreRef

    def getFirestoreRef(self):
        return self.__firestoreRef

    def isLax(self):
        return self.airportCode == 'LAX'

    def toDict(self):
        return {
            'coordinates': self.coordinates,
            'address': self.address,
            'airportCode': self.airportCode,
            'terminal': self.terminal
        }

    def __eq__(self, other):
        """
        Description:
            This method overrides python '==' operator and returns true if 
                this and the other location is identical. 
            Note that we are using python3 so overriding __neq__ is not necessary. 

            :param self: 
            :param other: 
        """
        if isinstance(other, AirportLocation):
            return (self.airportCode == other.airportCode) and (self.terminal == other.terminal)
