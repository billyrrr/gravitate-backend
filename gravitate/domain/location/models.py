import warnings

from google.cloud.firestore import Query

from flask_boiler import schema, fields, domain_model, attrs
from google.cloud.firestore_v1 import transactional

from gravitate import CTX
from gravitate.domain.driver_navigation.utils import get_coordinates, \
    get_address, gmaps, get_geocode

Schema = schema.Schema


# class CoordinateSchema(Schema):
#     latitude = fields.Raw(load_from="latitude", dump_to="latitude")
#     longitude = fields.Raw(load_from="longitude", dump_to="longitude")


# class LocationSchema(Schema):
#
#     coordinates = fields.Dict(missing=dict)
#     address = fields.Raw()


class Location(domain_model.DomainModel):
    coordinates = attrs.bdict()
    address = attrs.bproperty()

    @staticmethod
    def _to_address(coordinates):
        res = gmaps.reverse_geocode(
            latlng=(coordinates["latitude"],
                    coordinates["longitude"]),
            result_type=["route",]
        )
        return res[0]["formatted_address"]

    @address.getter
    def address(self):
        if not getattr(self, "_address", None):
            if self.coordinates:
                return self._to_address(self.coordinates)
            else:
                raise AttributeError
        else:
            return self._address

    @address.setter
    def address(self, value):
        self._address = value

    class Meta:
        # schema_cls = LocationSchema
        collection_name = "locations"

    def to_coordinate_str(self):
        return "{},{}".format(
            self.coordinates["latitude"], self.coordinates["longitude"])


# Location = SerializableClsFactory.create(
#     "Location", LocationSchema, base=Location)


# UserLocation = SerializableClsFactory.create(
#     "UserLocation",
#     UserLocationSchema,
#     base=Location)

class UserLocation(Location):

    sublocations = attrs.relation(nested=False, many=True, initialize=True)

    @sublocations.init
    def sublocations(self):
        self._attrs.sublocations = []

    place_id = attrs.bproperty(import_required=False, export_required=False)
    user_id = attrs.bproperty(import_required=False, export_required=False)

    @classmethod
    def add_sublocation(cls, location_id, sublocation_ids):
        transaction = CTX.db.transaction()

        @transactional
        def _add_sublocation_transactional(
                transaction, location_id, sublocation_ids):
            location = cls.get(doc_id=location_id, transaction=transaction)
            sublocations = list()
            for sublocation_id in sublocation_ids:
                sublocation = Location.get(
                    doc_id=sublocation_id,
                    transaction=transaction
                )
                sublocations.append(sublocation)
                location._add_sublocation(sublocation)

            location.save(transaction=transaction)
            # _ = [sublocation.save(transaction=transaction)
            #      for sublocation in sublocations ]

        return _add_sublocation_transactional(
            transaction=transaction,
            location_id=location_id,
            sublocation_ids=sublocation_ids
        )

    def _add_sublocation(self, sublocation):
        self.sublocations.append(sublocation.doc_ref)


class UserSublocation(Location):

    @classmethod
    def new(cls, *, latitude, longitude):
        res = gmaps.reverse_geocode(
            latlng=(latitude,
                    longitude),
            result_type=["route", ]
        )
        return super().new(
            coordinates={
                "latitude": res[0]["geometry"]["location"]["lat"],
                "longitude": res[0]["geometry"]["location"]["lng"]
            },
            address=res[0]["formatted_address"],
        )

    def to_view_dict(self):
        return dict(
            latitude=self.coordinates["latitude"],
            longitude=self.coordinates["longitude"],
            address=self.address
        )


# SocialEventLocation = SerializableClsFactory.create(
#     "SocialEventLocation",
#     SocialEventLocationSchema,
#     base=Location)


class SocialEventLocation(Location):
    event_name = attrs.bproperty()


class UcLocation(Location):
    campus_code = attrs.bproperty()
    campus_name = attrs.bproperty(requires=[super().address, campus_code])


class AirportLocation(Location):

    airport_code = attrs.bproperty()


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
        coordinates = get_coordinates(address=pickup_address)
        obj = UserLocation.new(coordinates=coordinates, address=pickup_address)
        return obj

    @staticmethod
    def from_place_address(address):
        g = get_geocode(address)

        latlng = g["geometry"]["location"]
        coordinates = {
            'latitude':     latlng["lat"],
            'longitude':    latlng["lng"]
        }

        obj = UserLocation.new(
            coordinates=coordinates,
            address=address,
            place_id=g["place_id"]
        )
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

