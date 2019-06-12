from flasgger import Schema, fields


class OrbitSchema(Schema):
    """
     "orbitCategory": "airportRide",
            "eventRef": "testeventref1",
            "userTicketPairs": {
            },
            "chatroomRef": "testchatroomref1",
            "costEstimate": 987654321,
            "status": 1
    TODO: implement
    """

    orbitCategory = fields.String()
    chatroomRef = fields.String()
    costEstimate = fields.Number()
    status = fields.Number()
