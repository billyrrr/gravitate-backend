from flask_restful import Resource

import gravitate.api_server.utils as service_utils
from gravitate.context import Context as CTX
from gravitate.domain.luggage import models

from flask_boiler import view

from functools import partial


luggages_doc_mapper = \
    partial(view.default_mapper, "rideRequests/{rideRequestId}/lcc/luggages_vm")


def register_luggages_service_new(app):

    view.document_as_view(app=app,
                          view_model_cls=models.Luggages,
                          endpoint="/rideRequests/<string:rideRequestId>/luggage",
                          mapper=luggages_doc_mapper)

