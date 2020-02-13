from flask_boiler import schema, fields, domain_model, view_model, view_mediator, mutation
from google.cloud.firestore_v1 import DocumentReference

from gravitate.domain.bookings.models import Target


class RideHostSchema(schema.Schema):

    from_location = fields.Relationship(nested=False)
    to_location = fields.Relationship(nested=False)

    target = fields.Embedded()

    user_id = fields.String()


class RideHost(domain_model.DomainModel):

    class Meta:
        schema_cls = RideHostSchema
        collection_name = "rideHosts"

    @property
    def target(self):
        if getattr(self, "_target", None) is None:
            self._target = Target.new()
        return self._target

    @target.setter
    def target(self, value):
        self._target = value


class RideHostViewSchema(schema.Schema):

    case_conversion = False

    from_location = fields.String()
    to_location = fields.String()
    earliest_arrival = fields.ISODatetime()
    latest_arrival = fields.ISODatetime()
    earliest_departure = fields.ISODatetime()
    latest_departure = fields.ISODatetime()
    user_id = fields.String()


def get_property(attr_name, inner_attr):
    def fget(self):
        inner = getattr(self, inner_attr)
        return getattr(inner, attr_name)

    def fset(self, value):
        inner = getattr(self, inner_attr)
        setattr(inner, attr_name, value)

    def fdel(self):
        inner = getattr(self, inner_attr)
        delattr(inner, attr_name)

    return property(fget=fget, fset=fset, fdel=fdel)


class RideHostView(view_model.ViewModel):

    class Meta:
        schema_cls = RideHostViewSchema

    def propagate_change(self):
        self.ride_host.save()

    earliest_departure = get_property("earliest_departure", "target")
    latest_departure = get_property("latest_departure", "target")
    earliest_arrival = get_property("earliest_arrival", "target")
    latest_arrival = get_property("latest_arrival", "target")

    @classmethod
    def new(cls, *args, **kwargs):
        return super().new(*args, **kwargs)

    @property
    def ride_host(self):
        if not getattr(self, "_ride_host", None):
            self._ride_host = RideHost.new()
        return self._ride_host

    @property
    def from_location(self):
        return self.ride_host.from_location

    @from_location.setter
    def from_location(self, value):
        self.ride_host.from_location = value

    @property
    def to_location(self):
        return self.ride_host.to_location

    @to_location.setter
    def to_location(self, value):
        self.ride_host.to_location = value

    @property
    def target(self):
        return self.ride_host.target

    @target.setter
    def target(self, value):
        self.ride_host.target = value

    @property
    def user_id(self):
        return self.ride_host.user_id

    @user_id.setter
    def user_id(self, value):
        self.ride_host.user_id = value

    # @property
    # def from_location(self):
    #     raise AttributeError
    #
    # @from_location.setter
    # def from_location(self, d):


class RideHostMutation(mutation.Mutation):

    view_model_cls = RideHostView

    @classmethod
    def mutate_create(cls, data=None):
        obj = cls.view_model_cls.from_dict(d=data)
        obj.propagate_change()
        return obj


class RHMediator(view_mediator.ViewMediator):

    pass



