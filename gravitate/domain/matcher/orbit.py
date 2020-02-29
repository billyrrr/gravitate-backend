from flask_boiler import schema, fields, domain_model

from gravitate.domain.bookings import RiderBooking
from gravitate.domain.host_car import RideHost


class OrbitSchema(schema.Schema):

    users = fields.Relationship(nested=False, many=True)
    bookings = fields.Relationship(nested=False, many=True)
    ride_host = fields.Relationship(nested=False, many=False)

    status = fields.Raw()


class OrbitBase(domain_model.DomainModel):

    class Meta:
        collection_name = "Orbit"


class Orbit(OrbitBase):

    class Meta:
        schema_cls = OrbitSchema

    def add_rider(self, rider_booking: RiderBooking):
        rider_booking.orbit_ref = self.doc_ref
        self.bookings.append(rider_booking.doc_ref)

        rider_booking.save()
        self.save()

    def add_host(self, ride_host: RideHost):
        ride_host.orbit_ref = self.doc_ref
        self.ride_host = ride_host.doc_ref

        ride_host.save()
        self.save()
