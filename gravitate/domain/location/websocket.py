from functools import partial

from flask_socketio import emit

from .models import UserSublocation
from .view_models import UserLocationView
from flask_boiler.view_model import ViewModel
from flask_boiler.view import WsMediator


class UserLocationWebsocket(UserLocationView):
    pass


class UserLocationWsMediator(WsMediator):

    def on_create_draft(self, data):
        sublocation = UserSublocation.new(
            latitude=data["latitude"],
            longitude=data["longitude"]
        )
        emit("draft_created", sublocation.to_view_dict())

