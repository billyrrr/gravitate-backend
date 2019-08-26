from flask_boiler import schema, fields, domain_model
from gravitate.domain.driver_navigation.utils import get_coordinates, \
    get_address

Schema = schema.Schema


# class CoordinateSchema(Schema):
#     latitude = fields.Raw(load_from="latitude", dump_to="latitude")
#     longitude = fields.Raw(load_from="longitude", dump_to="longitude")


class LocationSchema(Schema):

    coordinates = fields.Raw(load_from="coordinates",
                             dump_to="coordinates")
    address = fields.Raw(load_from="address",
                         dump_to="address")


class Location(domain_model.DomainModel):

    _schema_cls = LocationSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coordinates = dict()
        self.address = str()


class UserLocationSchema(LocationSchema):
    pass


class UserLocation(Location):

    _schema_cls = UserLocationSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SocialEventLocationSchema(LocationSchema):

    event_name = fields.Raw(
        load_from="eventName",
        dump_to="eventName")


class SocialEventLocation(Location):

    _schema_cls = SocialEventLocationSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_name = str()


class UcLocationSchema(LocationSchema):

    campus_code = fields.Raw(load_from="campusCode", dump_to="campusCode")
    campus_name = fields.Raw(load_from="campusName", dump_to="campusName")


class UcLocation(Location):

    _schema_cls = UcLocationSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campus_code = str()
        self.campus_name = str()


class AirportLocationSchema(LocationSchema):

    airport_code = fields.Raw(load_from="airportCode", dump_to="airportCode")


class AirportLocation(Location):

    _schema_cls = AirportLocationSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.airport_code = str()


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

