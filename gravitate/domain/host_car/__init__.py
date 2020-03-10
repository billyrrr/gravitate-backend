from math import inf

from flask_boiler import schema, fields, domain_model, view_model, mutation, \
    view_mediator
from flask_boiler.business_property_store import SimpleStore, BPSchema, \
    BusinessPropertyStore
from flask_boiler.schema import Schema
from flask_boiler.fields import Embedded, Integer, Relationship, Boolean, \
    String, Raw
from flask_boiler.domain_model import DomainModel
from flask_boiler.serializable import Serializable
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.struct import Struct
from flask_boiler.utils import get_property
from google.cloud.firestore import DocumentReference

from gravitate import CTX
from gravitate.domain.location import Location
from gravitate.domain.target import Target


class RideHostTarget(Target):

    class Meta:
        collection_name = "hostTargets"


class RideHostSchema(schema.Schema):

    from_location = fields.Relationship(nested=True)
    to_location = fields.Relationship(nested=True)

    target = fields.Relationship(nested=True)

    user_id = fields.String()
    orbit_ref = fields.Relationship(nested=False, required=False, allow_none=True)


class RideHost(domain_model.DomainModel):

    class Meta:
        schema_cls = RideHostSchema
        collection_name = "rideHosts"

    def save(self, *args, **kwargs):
        self.target.update_vals(with_dict=dict(
            r_ref=self.doc_ref,
            from_lat=self.from_location.coordinates["latitude"],
            from_lng=self.from_location.coordinates["longitude"],
            to_lat=self.to_location.coordinates["latitude"],
            to_lng=self.to_location.coordinates["longitude"]))
        return super().save(*args, **kwargs)

    @classmethod
    def new(cls, *args, target=None, **kwargs):
        if target is None:
            target = RideHostTarget.new()
        return super().new(*args, target=target, **kwargs)

    # @target.setter
    # def target(self, value):
    #     self._target = value


class RideHostViewSchema(schema.Schema):

    case_conversion = False

    from_location = fields.String()
    to_location = fields.String()
    earliest_arrival = fields.Localtime(default=-inf)
    latest_arrival = fields.Localtime(default=inf)
    earliest_departure = fields.Localtime(default=-inf)
    latest_departure = fields.Localtime(default=inf)
    user_id = fields.String()

    ride_host = fields.Raw(load_only=True, required=False)


class HostingStoreBpss(BPSchema):
    ride_host = fields.StructuralRef(dm_cls=RideHost)


class RideHostView(view_model.ViewModel):

    class Meta:
        schema_cls = RideHostViewSchema


class RideHostReadModel(RideHostView):

    class Meta:
        schema_cls = RideHostViewSchema

    earliest_departure = get_property("earliest_departure", "target")
    latest_departure = get_property("latest_departure", "target")
    earliest_arrival = get_property("earliest_arrival", "target")
    latest_arrival = get_property("latest_arrival", "target")

    @property
    def doc_ref(self):
        return CTX.db.document("users/{}/hostings/{}".format(self.user_id,
                                 self.store.ride_host.doc_id))

    @classmethod
    def new(cls, *args, snapshot=None, **kwargs):
        struct = Struct(schema_obj=HostingStoreBpss())
        struct["ride_host"] = (RideHost, snapshot.reference.id)

        container = SnapshotContainer()
        container.set(snapshot.reference._document_path, snapshot)

        store = BusinessPropertyStore(struct=struct,
                                      snapshot_container=container)
        store.refresh()
        return super().new(*args, store=store, **kwargs)

    @property
    def from_location(self):
        return self.store.ride_host.from_location.doc_ref.path

    @property
    def to_location(self):
        return self.store.ride_host.to_location.doc_ref.path

    @property
    def target(self):
        return self.store.ride_host.target

    @property
    def user_id(self):
        return self.store.ride_host.user_id


class RideHostForm(RideHostView):

    class Meta:
        schema_cls = RideHostViewSchema
    #
    # @property
    # def ride_host_id(self):
    #     return self.ride_host.doc_id
    #
    # @ride_host_id.setter
    # def ride_host_id(self, value):
    #     self.ride_host.doc_id = value

    def propagate_change(self):
        self.ride_host.save()

    @property
    def earliest_departure(self):
        raise AttributeError

    @earliest_departure.setter
    def earliest_departure(self, value):
        self.target.earliest_departure = value

    @property
    def latest_departure(self):
        raise AttributeError

    @latest_departure.setter
    def latest_departure(self, value):
        self.target.latest_departure = value

    @property
    def earliest_arrival(self):
        raise AttributeError

    @earliest_arrival.setter
    def earliest_arrival(self, value):
       self.target.earliest_arrival = value

    @property
    def latest_arrival(self):
        raise AttributeError

    @latest_arrival.setter
    def latest_arrival(self, value):
        self.target.latest_arrival = value

    @property
    def from_location(self):
        raise AttributeError

    @from_location.setter
    def from_location(self, value):
        if value != '':
            self.ride_host.from_location = Location.get(doc_ref_str=value)

    @property
    def to_location(self):
        raise AttributeError

    @to_location.setter
    def to_location(self, value):
        if value != '':
            self.ride_host.to_location = Location.get(doc_ref_str=value)

    @classmethod
    def new(cls, *args, doc_id=None, **kwargs):
        return super().new(*args, ride_host=RideHost.new(doc_id=doc_id),
                           **kwargs)

    @property
    def target(self) -> RideHostTarget:
        return self.ride_host.target

    @property
    def user_id(self):
        raise AttributeError

    @user_id.setter
    def user_id(self, value):
        self.ride_host.user_id = value

    #
    # @property
    # def ride_host(self):
    #     if not getattr(self, "_ride_host", None):
    #         self._ride_host = RiderBooking.new()
    #     return self._ride_host
    #
    # @ride_host.setter
    # def ride_host(self, value):
    #     self._ride_host = value


class RideHostMutation(mutation.Mutation):

    view_model_cls = RideHostForm

    @classmethod
    def mutate_create(cls, data=None):
        obj = cls.view_model_cls.from_dict(doc_id=data.get("doc_id", None),
                                           d=data)
        obj.propagate_change()
        return obj


class RHMediator(view_mediator.ViewMediator):

    pass
