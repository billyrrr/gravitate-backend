from functools import partial

from flask_socketio import emit

from .models import UserSublocation
from .view_models import UserLocationView
from flask_boiler.view_model import ViewModel
from flask_boiler.view_mediator_websocket import ViewMediatorWebsocket


class UserLocationWebsocket(UserLocationView):
    pass


class UserLocationWsMediator(ViewMediatorWebsocket):

    def on_create_draft(self, data):
        sublocation = UserSublocation.new(
            latitude=data["latitude"],
            longitude=data["longitude"]
        )
        emit("draft_created", sublocation.to_view_dict())

