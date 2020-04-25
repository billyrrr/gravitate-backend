from flask_boiler import schema, fields, domain_model, view_model, mutation, \
    view
from flask_boiler.business_property_store import SimpleStore, BPSchema, \
    BusinessPropertyStore
from flask_boiler.snapshot_container import SnapshotContainer
from flask_boiler.struct import Struct

from gravitate import CTX
from gravitate.domain.location import Location
from gravitate.domain.target import Target
from gravitate import common


class RiderTarget(Target):
    class Meta:
        collection_name = "riderTargets"


class RiderBookingSchema(schema.Schema):
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


class RiderBooking(domain_model.DomainModel):
    class Meta:
        schema_cls = RiderBookingSchema
        collection_name = "riderBookings"


class RiderBookingViewSchema(schema.Schema):

    rider_booking = fields.Raw(
        missing=fields.allow_missing, load_only=True, required=False)

    case_conversion = False

    from_location = fields.Raw(description="the origin of the trip")
    to_location = fields.Raw(description="the destination of the trip")

    earliest_arrival = fields.Localtime(allow_none=True)
    latest_arrival = fields.Localtime(allow_none=True)
    earliest_departure = fields.Localtime(allow_none=True)
    latest_departure = fields.Localtime(allow_none=True)

    user_id = fields.String(description="User Id (redundant)")

    preview_pic_url = fields.Raw(allow_none=True, description="Url of the preview picture of the origin and destination")
    localdate_timestamp = fields.Raw(allow_none=True, description="local time in timestamp (for sorting)")
    localdate_string = fields.Raw(allow_none=True, description="local time in iso8601 string")
    weekday = fields.Raw(allow_none=True, description="Return the day of the week as an integer, where Monday is 0 and Sunday is 6. For example, date(2002, 12, 4).weekday() == 2, a Wednesday")

    booking_id = fields.Raw(dump_only=True, description="Resource ID for booking (redundant)")


class BookingStoreBpss(BPSchema):
    rider_booking = fields.StructuralRef(dm_cls=RiderBooking)


class RiderBookingView(view_model.ViewModel):
    class Meta:
        schema_cls = RiderBookingViewSchema


class RiderBookingReadModel(RiderBookingView):
    class Meta:
        class schema_cls(schema.Schema):
            rider_booking = fields.Raw(
                missing=fields.allow_missing, load_only=True, required=False)

            case_conversion = False

            from_location = fields.Raw(description="the origin of the trip", dump_only=True)
            to_location = fields.Raw(description="the destination of the trip", dump_only=True)

            earliest_arrival = fields.Localtime(allow_none=True, dump_only=True)
            latest_arrival = fields.Localtime(allow_none=True, dump_only=True)
            earliest_departure = fields.Localtime(allow_none=True, dump_only=True)
            latest_departure = fields.Localtime(allow_none=True, dump_only=True)

            user_id = fields.String(description="User Id (redundant)", dump_only=True)

            preview_pic_url = fields.Raw(allow_none=True,
                                         description="Url of the preview picture of the origin and destination",
                                         dump_only=True)
            localdate_timestamp = fields.Raw(allow_none=True,
                                             description="local time in timestamp (for sorting)",
                                             dump_only=True)
            localdate_string = fields.Raw(allow_none=True,
                                          description="local time in iso8601 string",
                                          dump_only=True)
            weekday = fields.Raw(allow_none=True,
                                 description="Return the day of the week as an integer, where Monday is 0 and Sunday is 6. For example, date(2002, 12, 4).weekday() == 2, a Wednesday",
                                 dump_only=True)

            booking_id = fields.Raw(dump_only=True,
                                    description="Resource ID for booking (redundant)")


    @property
    def booking_id(self):
        return self.store.rider_booking.doc_id

    @property
    def doc_ref(self):
        return self._get_booking_ref(
            user_id=self.user_id,
            booking_id=self.booking_id
        )

    @classmethod
    def remove_one(cls, obj):
        doc_ref = cls._get_booking_ref(
            user_id=obj.user_id,
            booking_id=obj.doc_id
        )
        doc_ref.delete()

    @classmethod
    def _get_booking_ref(self, user_id, booking_id):
        return CTX.db.document(
            "users/{}/bookings/{}".format(user_id, booking_id))

    @classmethod
    def new(cls, *args, snapshot=None, doc_id=None, **kwargs):
        if snapshot is None:
            doc_ref = RiderBooking.ref_from_id(doc_id=doc_id)
            snapshot = CTX.db.document(doc_ref).get()
            return cls.new(*args, snapshot=snapshot, **kwargs)
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
        return self.store.rider_booking.from_location.to_dict()

    @property
    def to_location(self):
        return self.store.rider_booking.to_location.to_dict()

    @property
    def preview_pic_url(self):
        url="https://maps.googleapis.com/maps/api/staticmap?size=600x300&maptype=roadmap%20&markers=color:blue%7Clabel:S%7C{}&markers=color:red%7Clabel:E%7C{}%20&path=color:0x0000ff80|weight:10|geodesic:true|{}|{}&key=AIzaSyAeyQklNOdZGCNxSME0UpU-zntYPh9MY9E"
        return url.format(
            self.store.rider_booking.from_location.to_coordinate_str(),
            self.store.rider_booking.to_location.to_coordinate_str(),
            self.store.rider_booking.from_location.to_coordinate_str(),
            self.store.rider_booking.to_location.to_coordinate_str()
        )

    @property
    def user_id(self):
        return self.store.rider_booking.user_id

    @property
    def earliest_departure(self):
        val = self.store.rider_booking.earliest_departure
        if val is None:
            raise AttributeError
        return val

    @property
    def latest_departure(self):
        val = self.store.rider_booking.latest_departure
        if val is None:
            raise AttributeError
        return val

    @property
    def earliest_arrival(self):
        val = self.store.rider_booking.earliest_arrival
        if val is None:
            raise AttributeError
        return val

    @property
    def latest_arrival(self):
        val = self.store.rider_booking.latest_arrival
        if val is None:
            raise AttributeError
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


class RiderBookingForm(RiderBookingView):
    class Meta:
        schema_cls = RiderBookingViewSchema

    def propagate_change(self):
        self.rider_booking.save()

    @property
    def booking_id(self):
        return self.rider_booking.doc_id

    @property
    def from_location(self):
        raise AttributeError

    @from_location.setter
    def from_location(self, value):
        if value != '' and value is not None:
            if "/" in value:
                self.rider_booking.from_location = Location.get(doc_ref_str=value)
            else:
                self.rider_booking.from_location = Location.get(doc_id=value)

    @property
    def to_location(self):
        raise AttributeError

    @to_location.setter
    def to_location(self, value):
        if value != '' and value is not None:
            if "/" in value:
                self.rider_booking.to_location = Location.get(doc_ref_str=value)
            else:
                self.rider_booking.to_location = Location.get(doc_id=value)

    @classmethod
    def new(cls, *args, doc_id=None, **kwargs):
        # TODO: store string as constant
        return super().new(*args,
                           rider_booking=RiderBooking.new(
                               doc_id=doc_id, status="created"),
                           **kwargs)

    @property
    def user_id(self):
        raise AttributeError

    @user_id.setter
    def user_id(self, value):
        self.rider_booking.user_id = value

    @property
    def earliest_departure(self):
        raise AttributeError

    @earliest_departure.setter
    def earliest_departure(self, value):
        self.rider_booking.earliest_departure = value

    @property
    def latest_departure(self):
        raise AttributeError

    @latest_departure.setter
    def latest_departure(self, value):
        self.rider_booking.latest_departure = value

    @property
    def earliest_arrival(self):
        raise AttributeError

    @earliest_arrival.setter
    def earliest_arrival(self, value):
        self.rider_booking.earliest_arrival = value

    @property
    def latest_arrival(self):
        raise AttributeError

    @latest_arrival.setter
    def latest_arrival(self, value):
        self.rider_booking.latest_arrival = value


class RiderBookingMutation(mutation.Mutation):
    view_model_cls = RiderBookingForm

    @classmethod
    def mutate_create(cls, data=None):
        obj = cls.view_model_cls.new(doc_id=data.get("doc_id", None))
        obj.update_vals(with_raw=data)
        obj.propagate_change()
        return obj

    @classmethod
    def mutate_delete(cls, doc_id=None):
        # TODO: store string as constant
        obj = RiderBooking.get(doc_id=doc_id)
        obj.status = "removed"
        obj.save()
        return obj


class RBMediator(view.RestMediator):
    pass
