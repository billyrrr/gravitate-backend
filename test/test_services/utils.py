from test.store import FormDictFactory
from test.test_main import getMockAuthHeaders


def _create_ride_requests_for_tests(app, userIds, to_tear_down, rideRequestIds):

    for userId in userIds:

        form = FormDictFactory().create(returnDict=True)
        form["flightLocalTime"] = "2018-12-20T12:00:00.000"
        r = app.post(path='/rideRequests',
                     json=form,
                     headers=getMockAuthHeaders(uid=userId)
                     )
        print(r.data)
        assert r.status_code == 200
        rideRequestIds.append(r.json["firestoreRef"])
        to_tear_down.append((userId, r.json["firestoreRef"]))