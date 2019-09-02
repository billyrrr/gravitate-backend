import warnings

from google.cloud.firestore import Query

from flask_boiler import schema, fields, domain_model
from flask_boiler.serializable import SerializableClsFactory
from gravitate.domain.driver_navigation.utils import get_coordinates, \
    get_address

Schema = schema.Schema


# class CoordinateSchema(Schema):
#     latitude = fields.Raw(load_from="latitude", dump_to="latitude")
#     longitude = fields.Raw(load_from="longitude", dump_to="longitude")


class LocationDomainModelBase(domain_model.DomainModel):

    _collection_name = "locations"


class LocationSchema(Schema):

    coordinates = fields.Raw(load_from="coordinates",
                             dump_to="coordinates")
    address = fields.Raw(load_from="address",
                         dump_to="address")


Location = SerializableClsFactory.create(
    "Location", LocationSchema, base=LocationDomainModelBase)


class UserLocationSchema(LocationSchema):
    pass


UserLocation = SerializableClsFactory.create(
    "UserLocation", UserLocationSchema, base=Location)


class SocialEventLocationSchema(LocationSchema):

    event_name = fields.Raw(
        load_from="eventName",
        dump_to="eventName")


SocialEventLocation = SerializableClsFactory.create(
    "SocialEventLocation",
    SocialEventLocationSchema,
    base=Location)


class UcLocationSchema(LocationSchema):

    campus_code = fields.Raw(load_from="campusCode", dump_to="campusCode")
    campus_name = fields.Raw(load_from="campusName", dump_to="campusName")


UcLocation = SerializableClsFactory.create(
    "UcLocation", UcLocationSchema, base=Location
)


class AirportLocationSchema(LocationSchema):

    airport_code = fields.Raw(load_from="airportCode", dump_to="airportCode")


AirportLocation = SerializableClsFactory.create(
    "AirportLocation", AirportLocationSchema, base=Location
)


campus_code_table = {
    "UCSB": {
        "obj_type": "UcLocation",
        "coordinates": {
            "latitude": 34.414132,
            "longitude": -119.848868
        },
        "address": "C572+HC Isla Vista, California",
        "campusName": "University of California, Santa Barbara",
        "campusCode": "UCSB"
    }
}


class LocationFactory:

    @staticmethod
    def from_pickup_address(pickup_address):
        coordinates = get_coordinates(pickup_address)
        obj = UserLocation.create()
        obj.coordinates = coordinates
        obj.address = pickup_address
        return obj

    @staticmethod
    def from_code(code, location_category="campus"):
        if location_category == "campus" and code in campus_code_table.keys():
            return UcLocation.from_dict(campus_code_table[code])

    @staticmethod
    def from_fb_place(d):
        """
        Create location with facebook event - place
        Example: {
                "name": "Coachella",
                "location": {
                    "latitude": 33.679974,
                    "longitude": -116.237221
                },
                "id": "20281766647"
            }
        :return:
        """
        address = get_address(d["location"])

        obj = SocialEventLocation.create()

        obj.coordinates=d["location"]
        obj.address=address
        obj.event_name=d["name"]

        return obj


class LocationQuery(Location):

    @classmethod
    def find_by_airport_code(cls, airportCode) -> AirportLocation:
        airportLocations = list( Location.where(airportCode=airportCode) )
        if len(airportLocations) != 1:
            location_ids = [obj.doc_ref.path for obj in airportLocations]
            raise ValueError(
                "Airport Location that has the airport code"
                " is not unique or does not exist: {}".format(
                    " ".join(location_ids)
                    ))
        result = airportLocations.pop()
        return result

    @classmethod
    def find_by_campus_code(self, campusCode) -> UcLocation:
        campus_locations = list( Location.where(campusCode=campusCode) )
        if len(campus_locations) != 1:
            warnings.warn(
                "Campus Location that has the campus code is not unique or does not exist: {}".format(
                    campus_locations))
            return None

        result = campus_locations.pop()
        return result

