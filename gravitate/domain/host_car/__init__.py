from flask_boiler import schema, fields, domain_model, view_model, view_mediator, mutation
from google.cloud.firestore_v1 import DocumentReference


class RideHostSchema(schema.Schema):

    from_location = fields.Relationship(nested=False)
    to_location = fields.Relationship(nested=False)

    target = fields.Raw()

    user_id = fields.String()


class RideHost(domain_model.DomainModel):

    class Meta:
        schema_cls = RideHostSchema
        collection_name = "rideHosts"


class RideHostViewSchema(schema.Schema):

    from_location = fields.String()
    to_location = fields.String()
    target = fields.Raw()
    user_id = fields.String()


class RideHostView(view_model.ViewModel):

    class Meta:
        schema_cls = RideHostViewSchema

    def propagate_change(self):
        self.ride_host.save()

    @classmethod
    def new(cls, *args, doc_id=None, **kwargs):
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
        obj = cls.view_model_cls.new(**data)
        obj.propagate_change()
        return obj


class RHMediator(view_mediator.ViewMediator):

    pass



