from google.cloud.firestore import transactional, Transaction
from .models import Luggages
from gravitate.data_access import RideRequestGenericDao
from gravitate.context import Context

db = Context.db


def put_luggages(ride_request_id, luggages: Luggages):
    transaction = db.transaction()
    _put_luggages_transactional(transaction=transaction, ride_request_id=ride_request_id, luggages=luggages)


@transactional
def _put_luggages_transactional(transaction: Transaction, ride_request_id, luggages: Luggages):
    ride_request_ref = RideRequestGenericDao().ref_from_id(ride_request_id)
    ride_request = RideRequestGenericDao().get_with_transaction(
        transaction=transaction, rideRequestRef=ride_request_ref)
    ride_request.baggages = luggages.to_dict()
    RideRequestGenericDao().set_with_transaction(
        transaction=transaction, rideRequestRef=ride_request_ref, newRideRequest=ride_request)
