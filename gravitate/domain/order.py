from flask_boiler import attrs
from flask_boiler.domain_model import DomainModel
from flask_boiler.models.base import Serializable


class Place(Serializable):

    address = attrs.bproperty()
    latitude = attrs.bproperty()
    longitude = attrs.bproperty()

    class Meta:
        case_conversion = False
        exclude = ("obj_type", "doc_id", "doc_ref")


class Dropoff(Place):
    pass


class Pickup(Place):
    pass


class Driver(Serializable):
    """
    "device_id": "",
     "id": obj._driver.user._id,
     "name": obj._driver.name,
     "phone_number": "",
     "role": "rider"
    """

    class Meta:
        case_conversion = False
        exclude = ("obj_type", "doc_id", "doc_ref")

    device_id = attrs.bproperty()
    _id = attrs.bproperty(data_key="id")
    name = attrs.bproperty()
    phone_number = attrs.bproperty()
    role = attrs.bproperty()

    @role.getter
    def role(self):
        return "driver"


class Rider(Serializable):
    """
    "device_id": "",
                     "id": obj._driver.user._id,
                     "name": obj._driver.name,
                     "phone_number": "",
                     "role": "rider"
    """
    device_id = attrs.bproperty()
    _id = attrs.bproperty(data_key="id")
    name = attrs.bproperty()
    phone_number = attrs.bproperty()
    role = attrs.bproperty()

    class Meta:
        case_conversion = False
        exclude = ("obj_type", "doc_id", "doc_ref")

    @role.getter
    def role(self):
        return "rider"


status_from_typ = dict(NewOrder="NEW")
typ_from_status = dict(NEW="NewOrder")


class Order(DomainModel):
    """

    "created_at": "2019-11-07T21:50:12+00:00",
    "status": "NEW",
    "dropoff": {
      "address": null,
      "latitude": 47.84284957575306,
      "longitude": 35.10294444859028
    },
    "pickup": {
      "address": null,
      "latitude": 47.835803,
      "longitude": 35.11009362
    },
    "rider": {
      "role": "rider",
      "device_id": null,
      "name": "Ms. Rider",
      "phone_number": null
    }

    """

    class Meta:
        case_conversion = False
        exclude = ("obj_type", "doc_id", "doc_ref")

    created_at = attrs.bproperty()
    status = attrs.bproperty()

    rider = attrs.embed(obj_cls=Rider)
    driver = attrs.embed(obj_cls=Driver)

    dropoff = attrs.embed(obj_cls=Dropoff)
    pickup = attrs.embed(obj_cls=Pickup)
