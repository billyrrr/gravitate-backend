import flask_socketio

from gravitate.domain.location import Location
from gravitate.domain.location.websocket import UserLocationWsMediator, \
    UserLocationWebsocket


def test_view_websocket():
    from gravitate.main import app

    mediator = UserLocationWsMediator(
        view_model_cls=UserLocationWebsocket,
        namespace="/sublocations"
    )

    print(Location.get_schema_obj().fields)

    io = flask_socketio.SocketIO(app=app)
    io.on_namespace(mediator)

    client = io.test_client(app=app, namespace='/sublocations')

    assert client.is_connected(namespace='/sublocations')

    _ = client.emit('create_draft',
                    {
                        "user_id": "test_user_id1",
                        "latitude": 32.879707,
                        "longitude": -117.241254
                    },
                    namespace='/sublocations')

    res = client.get_received(namespace="/sublocations")
    assert res[-1] == {'name': 'draft_created', 'args': [
        {'latitude': 32.879707,
         'longitude': -117.241254,
         'address': 'Muir Ln, San Diego, CA 92161, USA'}],
                       'namespace': '/sublocations'}
