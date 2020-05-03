from flask_boiler.view_model import ViewModel
from flask_boiler import attrs

from gravitate.domain.location.models import Sublocation


class CoriderView(ViewModel):

    user = attrs.bproperty(import_required=True, export_enabled=False)
    booking = attrs.bproperty(import_required=True, export_enabled=False)
    pickup_location: Sublocation = attrs.bproperty(import_required=True, export_enabled=False)
    dropoff_location = attrs.bproperty(import_required=True, export_enabled=False)

    name = attrs.bproperty()
    pickup_address = attrs.bproperty()
    dropoff_address = attrs.bproperty()

    @pickup_address.getter
    def pickup_address(self):
        return self.pickup_location.road_name

    @dropoff_address.getter
    def dropoff_address(self):
        return self.dropoff_location.road_name

    @name.getter
    def name(self):
        return self.user.name


class RideHostUserView(ViewModel):

    user = attrs.bproperty(import_required=True, export_enabled=False)

    name = attrs.bproperty()

    @name.getter
    def name(self):
        return self.user.name
