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
    def from_dict(location_dict):
        coordinates = location_dict['coordinates']
        address = location_dict['address']
        location_category = location_dict['locationCategory']
        if location_category == 'airport':
            airport_code = location_dict['airportCode']
            return AirportLocation(coordinates, address, airport_code)
        elif location_category == 'social':
            event_name = location_dict['eventName']
            return SocialEventLocation(coordinates, address, event_name)
        elif location_category == 'campus':
            campus_code = location_dict['campusCode']
            campus_name = location_dict['campusName']
            coordinates = location_dict['coordinates']
            address = location_dict['address']
            return UcLocation(coordinates, address, campus_name, campus_code)
        else:
            raise NotImplementedError(
                'Unsupported locationCategory ' + str(location_category) + '. ')
                
        return Location(coordinates, address)

    @staticmethod
    def from_code(code, location_category="campus"):
        if location_category == "campus" and code in campus_code_table.keys():
            return Location.from_dict(campus_code_table[code])
        raise NotImplementedError
    
    def to_dict(self) -> dict:
        return {
            'coordinates': self.coordinates,
            'address': self.address
        }


campus_code_table = {
    "UCSB": {
        "locationCategory": "campus",
        "coordinates": {
            "latitude": 34.414132,
            "longitude": -119.848868
        },
        "address": "C572+HC Isla Vista, California",
        "campusName": "University of California, Santa Barbara",
        "campusCode": "UCSB"
    }
}


class SocialEventLocation(Location):
    def __init__(self, coordinates, address, event_name):
        super().__init__(coordinates, address)
        self.location_category = 'social'
        self.event_name = event_name

    def to_dict(self):
        return {
            'locationCategory': self.location_category,
            'coordinates': self.coordinates,
            'address': self.address,
            'eventName': self.event_name
        }


class UcLocation(Location):
    """ Description
        This class represents a UC campus in another city.
    """

    def __init__(self, coordinates, address, campus_name, campus_code):
        super().__init__(coordinates, address)
        self.location_category = 'campus'
        self.campus_name = campus_name
        self.campus_code = campus_code

    def to_dict(self):
        return {
            'locationCategory': self.location_category,
            'coordinates': self.coordinates,
            'address': self.address,
            'campusName': self.campus_name,
            'campusCode': self.campus_code,
        }


class AirportLocation(Location):
    """
    Description
        This class represents an airport location.
        Two airport locations are considered the same if 
            their airportCode (ie. "LAX") 
            are identical. 

    """

    def __init__(self, coordinates, address, airport_code):
        super().__init__(coordinates, address)
        self.location_category = 'airport'
        self.airport_code = airport_code

    def is_lax(self):
        return self.airport_code == 'LAX'

    def to_dict(self):
        return {
            'locationCategory': self.location_category,
            'coordinates': self.coordinates,
            'address': self.address,
            'airportCode': self.airport_code,
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
            return (self.airport_code == other.airport_code)
    