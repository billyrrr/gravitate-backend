from .firestore_object import FirestoreObject

class Location(FirestoreObject):

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
            airportCode = locationDict['airportCode']
            return AirportLocation(coordinates, address, airportCode)
        elif locationCategory == 'social':
            raise NotImplementedError(
                'Social event location is not yet implemented.')
        elif locationCategory == 'campus':
            campusCode = locationDict['campusCode']
            campusName = locationDict['campusName']
            coordinates = locationDict['coordinates']
            address = locationDict['address']
            return AirportLocation(coordinates, address, campusName, campusCode)
        else:
            raise NotImplementedError(
                'Unsupported locationCategory ' + str(locationCategory) + '. ')
                
        return Location(coordinates, address)

    @staticmethod
    def fromCode(code, locationCategory="campus"):
        if locationCategory == "campus" and code in campusCodeTable.keys():
            return Location.fromDict(campusCodeTable[code])
        raise NotImplementedError
    
    def toDict(self) -> dict:
        return {
            'coordinates': self.coordinates,
            'address': self.address
        }

campusCodeTable = {
    "UCSB": {
        "coordinates": {
            "latitude": 34.414132,
            "longitude": -119.848868
        },
        "address": "C572+HC Isla Vista, California",
        "campusName": "University of California, Santa Barbara",
        "campusCode": "UCSB"
    }
}


class UcLocation(Location):
    """ Description
        This class represents a UC campus in another city.
    """

    def __init__(self, coordinates, address, campusName, campusCode):
        super().__init__(coordinates, address)
        self.locationCategory = 'campus'
        self.campusName = campusName
        self.campusCode = campusCode

    def toDict(self):
        return {
            'locationCategory': self.locationCategory,
            'coordinates': self.coordinates,
            'address': self.address,
            'campusName': self.campusName,
            'campusCode': self.campusCode,
        }


class AirportLocation(Location):
    """
    Description
        This class represents an airport location.
        Two airport locations are considered the same if 
            their airportCode (ie. "LAX") 
            are identical. 

    """

    def __init__(self, coordinates, address, airportCode):
        super().__init__(coordinates, address)
        self.locationCategory = 'airport'
        self.airportCode = airportCode

    def isLax(self):
        return self.airportCode == 'LAX'

    def toDict(self):
        return {
            'locationCategory': self.locationCategory, 
            'coordinates': self.coordinates,
            'address': self.address,
            'airportCode': self.airportCode,
        }

    def __eq__(self, other):
        """
        Description
            This method overrides python '==' operator and returns true if 
                this and the other location is identical. 
            Note that we are using python3 so overriding __neq__ is not necessary. 

            :param self: 
            :param other: 
        """
        if isinstance(other, AirportLocation):
            return (self.airportCode == other.airportCode) 