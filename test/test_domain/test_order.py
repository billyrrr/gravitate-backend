import pytest

from gravitate.domain.order import Order, Rider, Driver


def test_from_dict():
    d = {"created_at": "2019-11-07T21:50:12+00:00",
         "status": "NEW",
         "dropoff": {
             "address": None,
             "latitude": 47.84284957575306,
             "longitude": 35.10294444859028
         },
         "pickup": {
             "address": None,
             "latitude": 47.835803,
             "longitude": 35.11009362
         },
         "rider": {
             "role": "rider",
             "device_id": None,
             "name": "Ms. Rider",
             "phone_number": None
         }}

    order = Order.from_dict(d)

    assert isinstance(order.rider, Rider)

    assert order.to_dict() == d
