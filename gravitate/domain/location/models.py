import warnings

from google.cloud.firestore import Query

from flask_boiler import schema, fields, domain_model
from gravitate.domain.driver_navigation.utils import get_coordinates, \
    get_address

Schema = schema.Schema


# class CoordinateSchema(Schema):
#     latitude = fields.Raw(load_from="latitude", dump_to="latitude")
#     longitude = fields.Raw(load_from="longitude", dump_to="longitude")


class LocationSchema(Schema):

    coordinates = fields.Raw()
    address = fields.Raw()


class Location(domain_model.DomainModel):

    class Meta:
        collection_name = "locations"


# Location = SerializableClsFactory.create(
#     "Location", LocationSchema, base=Location)


class UserLocationSchema(LocationSchema):
    pass


# UserLocation = SerializableClsFactory.create(
#     "UserLocation",
#     UserLocationSchema,
#     base=Location)

class UserLocation(Location):

    class Meta:
        schema_cls = UserLocationSchema


class SocialEventLocationSchema(LocationSchema):

    event_name = fields.Raw()


# SocialEventLocation = SerializableClsFactory.create(
#     "SocialEventLocation",
#     SocialEventLocationSchema,
#     base=Location)


class SocialEventLocation(Location):

    class Meta:
        schema_cls = SocialEventLocationSchema


class UcLocationSchema(LocationSchema):

    campus_code = fields.Raw()
    campus_name = fields.Raw()


# UcLocation = SerializableClsFactory.create(
#     "UcLocation",
#     UcLocationSchema,
#     base=Location
# )


class UcLocation(Location):

    class Meta:
        schema_cls = UcLocationSchema


class AirportLocationSchema(LocationSchema):

    airport_code = fields.Raw()

#
# AirportLocation = SerializableClsFactory.create(
#     "AirportLocation",
#     AirportLocationSchema,
#     base=Location
# )


class AirportLocation(Location):

    class Meta:
        schema_cls = AirportLocationSchema


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
        obj = UserLocation.new(coordinates=coordinates, address=pickup_address)
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

        obj = SocialEventLocation.new(
            coordinates=d["location"],
            address=address,
            event_name=d["name"]
        )
        #
        # obj.coordinates=d["location"]
        # obj.address=address
        # obj.event_name=d["name"]

        return obj


class LocationQuery(Location):

    @classmethod
    def find_by_airport_code(cls, airportCode) -> AirportLocation:
        airportLocations = list(AirportLocation.where(airport_code=airportCode))
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
        campus_locations = list(UcLocation.where(campus_code=campusCode))
        if len(campus_locations) != 1:
            warnings.warn(
                "Campus Location that has the campus code is not unique or does not exist: {}".format(
                    campus_locations))
            return None

        result = campus_locations.pop()
        return result

