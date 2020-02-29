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


class RiderTarget(Target):

    class Meta:
        collection_name = "riderTargets"


class RiderBookingSchema(schema.Schema):

    from_location = fields.Relationship(nested=True)
    to_location = fields.Relationship(nested=True)

    target = fields.Relationship(nested=True)

    user_id = fields.String()
    orbit_ref = fields.Relationship(nested=False, required=False, allow_none=True)


class RiderBooking(domain_model.DomainModel):

    class Meta:
        schema_cls = RiderBookingSchema
        collection_name = "riderBookings"

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
            target = RiderTarget.new()
        return super().new(*args, target=target, **kwargs)

    # @target.setter
    # def target(self, value):
    #     self._target = value


class RiderBookingViewSchema(schema.Schema):

    case_conversion = False

    from_location = fields.String()
    to_location = fields.String()
    earliest_arrival = fields.Localtime(allow_none=True, missing=-inf)
    latest_arrival = fields.Localtime(allow_none=True, missing=inf)
    earliest_departure = fields.Localtime(allow_none=True, missing=-inf)
    latest_departure = fields.Localtime(allow_none=True, missing=inf)
    user_id = fields.String()

    rider_booking = fields.Raw(load_only=True, required=False)


class BookingStoreBpss(BPSchema):
    rider_booking = fields.StructuralRef(dm_cls=RiderBooking)


class BookingStore(SimpleStore):

    def __init__(self, booking):
        self.rider_booking = booking


class RiderBookingView(view_model.ViewModel):

    class Meta:
        schema_cls = RiderBookingViewSchema


class RiderBookingReadModel(RiderBookingView):

    class Meta:
        schema_cls = RiderBookingViewSchema

    earliest_departure = get_property("earliest_departure", "target")
    latest_departure = get_property("latest_departure", "target")
    earliest_arrival = get_property("earliest_arrival", "target")
    latest_arrival = get_property("latest_arrival", "target")

    @property
    def doc_ref(self):
        return CTX.db.document("users/{}/bookings/{}".format(self.user_id,
                                 self.store.rider_booking.doc_id))

    @classmethod
    def new(cls, *args, snapshot=None, **kwargs):
        struct = Struct(schema_obj=BookingStoreBpss())
        struct["rider_booking"] = (RiderBooking, snapshot.reference.id)

        container = SnapshotContainer()
        container.set(snapshot.reference._document_path, snapshot)

        store = BusinessPropertyStore(struct=struct,
                                      snapshot_container=container)
        store.refresh()
        return super().new(*args, store=store, **kwargs)

    @property
    def from_location(self):
        return self.store.rider_booking.from_location.doc_ref.path

    @property
    def to_location(self):
        return self.store.rider_booking.to_location.doc_ref.path

    @property
    def target(self):
        return self.store.rider_booking.target

    @property
    def user_id(self):
        return self.store.rider_booking.user_id


class RiderBookingForm(RiderBookingView):

    class Meta:
        schema_cls = RiderBookingViewSchema

    def propagate_change(self):
        self.rider_booking.save()

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
            self.rider_booking.from_location = Location.get(doc_ref_str=value)

    @property
    def to_location(self):
        raise AttributeError

    @to_location.setter
    def to_location(self, value):
        if value != '':
            self.rider_booking.to_location = Location.get(doc_ref_str=value)

    @classmethod
    def new(cls, *args, doc_id=None, **kwargs):
        return super().new(*args, rider_booking=RiderBooking.new(doc_id=doc_id),
                           **kwargs)

    @property
    def target(self) -> RiderTarget:
        return self.rider_booking.target

    @property
    def user_id(self):
        raise AttributeError

    @user_id.setter
    def user_id(self, value):
        self.rider_booking.user_id = value

    #
    # @property
    # def rider_booking(self):
    #     if not getattr(self, "_rider_booking", None):
    #         self._rider_booking = RiderBooking.new()
    #     return self._rider_booking
    #
    # @rider_booking.setter
    # def rider_booking(self, value):
    #     self._rider_booking = value


class RiderBookingMutation(mutation.Mutation):

    view_model_cls = RiderBookingForm

    @classmethod
    def mutate_create(cls, data=None):
        obj = cls.view_model_cls.from_dict(doc_id=data["doc_id"], d=data)
        obj.propagate_change()
        return obj


class RBMediator(view_mediator.ViewMediator):

    pass
