from flask_boiler import schema, fields, domain_model, view_model, view_mediator, mutation
from google.cloud.firestore_v1 import DocumentReference

from gravitate.domain.bookings.models import Target
from gravitate.domain.location import Location


class RideHostTarget(Target):
    pass


class RideHostSchema(schema.Schema):

    from_location = fields.Relationship(nested=True)
    to_location = fields.Relationship(nested=True)

    target = fields.Relationship(nested=True)

    user_id = fields.String()


class RideHost(domain_model.DomainModel):

    class Meta:
        schema_cls = RideHostSchema
        collection_name = "rideHosts"

    @property
    def target(self):
        if getattr(self, "_target", None) is None:
            #         "coordinates": {
            #             "latitude": 34.414132,
            #             "longitude": -119.848868
            #         },
            self._target = RideHostTarget.new(
                r_ref=self.doc_ref
            )
        return self._target

    def save(self, *args, **kwargs):
        self.target.update_vals(with_dict=dict(
            from_lat=self.from_location.coordinates["latitude"],
            from_lng=self.from_location.coordinates["longitude"],
            to_lat=self.to_location.coordinates["latitude"],
            to_lng=self.to_location.coordinates["longitude"]))
        return super().save(*args, **kwargs)

    @target.setter
    def target(self, value):
        self._target = value


class RideHostViewSchema(schema.Schema):

    case_conversion = False

    from_location = fields.String()
    to_location = fields.String()
    earliest_arrival = fields.Localtime()
    latest_arrival = fields.Localtime()
    earliest_departure = fields.Localtime()
    latest_departure = fields.Localtime()
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
        return self.ride_host.from_location.doc_ref

    @from_location.setter
    def from_location(self, value):
        if value != '':
            self.ride_host.from_location = Location.get(doc_ref_str=value)

    @property
    def to_location(self):
        return self.ride_host.to_location.doc_ref

    @to_location.setter
    def to_location(self, value):
        if value != '':
            self.ride_host.to_location = Location.get(doc_ref_str=value)

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



