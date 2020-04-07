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
from google.cloud.firestore import DocumentReference

from gravitate import CTX, common
from gravitate.domain.location import Location
from gravitate.domain.target import Target


class RideHostTarget(Target):

    class Meta:
        collection_name = "hostTargets"


class RideHostSchema(schema.Schema):
    from_location = fields.Relationship(nested=True)
    to_location = fields.Relationship(nested=True)

    earliest_arrival = fields.Raw(allow_none=True)
    latest_arrival = fields.Raw(allow_none=True)
    earliest_departure = fields.Raw(allow_none=True)
    latest_departure = fields.Raw(allow_none=True)

    user_id = fields.String()
    orbit_ref = fields.Relationship(nested=False, required=False,
                                    allow_none=True)

    status = fields.Raw()

class RideHost(domain_model.DomainModel):

    class Meta:
        schema_cls = RideHostSchema
        collection_name = "rideHosts"


class RideHostViewSchema(schema.Schema):
    case_conversion = False

    ride_host = fields.Raw(
        missing=fields.allow_missing, load_only=True, required=False)

    from_location = fields.Raw()
    to_location = fields.Raw()

    earliest_arrival = fields.Localtime(allow_none=True)
    latest_arrival = fields.Localtime(allow_none=True)
    earliest_departure = fields.Localtime(allow_none=True)
    latest_departure = fields.Localtime(allow_none=True)

    user_id = fields.String()

    preview_pic_url = fields.Raw(allow_none=True)
    localdate_timestamp = fields.Raw(allow_none=True, description="local time in timestamp (for sorting)")
    localdate_string = fields.Raw(allow_none=True, description="local time in iso8601 string")
    weekday = fields.Raw(allow_none=True, description="Return the day of the week as an integer, where Monday is 0 and Sunday is 6. For example, date(2002, 12, 4).weekday() == 2, a Wednesday")

    hosting_id = fields.Raw(dump_only=True)


class HostingStoreBpss(BPSchema):
    ride_host = fields.StructuralRef(dm_cls=RideHost)


class RideHostView(view_model.ViewModel):

    class Meta:
        schema_cls = RideHostViewSchema


class RideHostReadModel(RideHostView):

    class Meta:
        schema_cls = RideHostViewSchema

    @property
    def hosting_id(self):
        return self.store.ride_host.doc_id

    @property
    def doc_ref(self):
        return self._get_hosting_ref(
            user_id=self.user_id,
            hosting_id=self.hosting_id
        )

    @classmethod
    def remove_one(cls, obj):
        doc_ref = cls._get_hosting_ref(
            user_id=obj.user_id,
            hosting_id=obj.doc_id
        )
        doc_ref.delete()

    @classmethod
    def _get_hosting_ref(self, user_id, hosting_id):
        return CTX.db.document("users/{}/hostings/{}".format(
            user_id, hosting_id))

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
        return self.store.ride_host.from_location.to_dict()

    @property
    def to_location(self):
        return self.store.ride_host.to_location.to_dict()

    @property
    def preview_pic_url(self):
        url = "https://maps.googleapis.com/maps/api/staticmap?size=600x300&maptype=roadmap%20&markers=color:blue%7Clabel:S%7C{}&markers=color:red%7Clabel:E%7C{}%20&path=color:0x0000ff80|weight:10|geodesic:true|{}|{}&key=AIzaSyAeyQklNOdZGCNxSME0UpU-zntYPh9MY9E"
        return url.format(
            self.store.ride_host.from_location.to_coordinate_str(),
            self.store.ride_host.to_location.to_coordinate_str(),
            self.store.ride_host.from_location.to_coordinate_str(),
            self.store.ride_host.to_location.to_coordinate_str()
        )

    @property
    def isoweekday(self):
        """
        TODO: add read weekday from other time attributes
        :return:
        """
        val = common.local_dt_from_timestamp(self.earliest_departure)
        return val.isoweekday()

    @property
    def user_id(self):
        return self.store.ride_host.user_id

    @property
    def earliest_departure(self):
        val = self.store.ride_host.earliest_departure
        return val

    @property
    def latest_departure(self):
        val = self.store.ride_host.latest_departure
        return val

    @property
    def earliest_arrival(self):
        val = self.store.ride_host.earliest_arrival
        return val

    @property
    def latest_arrival(self):
        val = self.store.ride_host.latest_arrival
        return val

    @property
    def localdate_timestamp(self):
        return self.earliest_departure

    @property
    def localdate_string(self):
        return common.local_dt_from_timestamp(self.localdate_timestamp)\
            .isoformat()

    @property
    def weekday(self):
        """
        TODO: add read weekday from other time attributes
        :return:
        """
        val = common.local_dt_from_timestamp(self.localdate_timestamp)
        return val.weekday()


class RideHostForm(RideHostView):

    class Meta:
        schema_cls = RideHostViewSchema

    @property
    def hosting_id(self):
        return self.ride_host.doc_id

    def propagate_change(self):
        self.ride_host.save()

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
        return super().new(*args,
                           ride_host=RideHost.new(
                               doc_id=doc_id, status="created"),
                           **kwargs)

    @property
    def user_id(self):
        raise AttributeError

    @user_id.setter
    def user_id(self, value):
        self.ride_host.user_id = value

    @property
    def earliest_departure(self):
        raise AttributeError

    @earliest_departure.setter
    def earliest_departure(self, value):
        self.ride_host.earliest_departure = value

    @property
    def latest_departure(self):
        raise AttributeError

    @latest_departure.setter
    def latest_departure(self, value):
        self.ride_host.latest_departure = value

    @property
    def earliest_arrival(self):
        raise AttributeError

    @earliest_arrival.setter
    def earliest_arrival(self, value):
        self.ride_host.earliest_arrival = value

    @property
    def latest_arrival(self):
        raise AttributeError

    @latest_arrival.setter
    def latest_arrival(self, value):
        self.ride_host.latest_arrival = value


class RideHostMutation(mutation.Mutation):
    view_model_cls = RideHostForm

    @classmethod
    def mutate_create(cls, data=None):
        obj = cls.view_model_cls.new(doc_id=data.get("doc_id", None))
        obj.update_vals(with_raw=data)
        obj.propagate_change()
        return obj

    @classmethod
    def mutate_delete(cls, doc_id=None):
        # TODO: store string as constant
        obj = RideHost.get(doc_id=doc_id)
        obj.status = "removed"
        obj.save()
        return obj


class RHMediator(view_mediator.ViewMediator):

    pass
