from flask_restful import HTTPException

errors = {
    'RequestAlreadyMatchedError': {
        "message": "Ride request has requestCompletion as True. Un-match from an orbit first. ",
        "status": 500
    },
    'RequestAlreadyExistsError': {
        "message": "Ride request on the same day (or for the same event) already exists",
        "status": 400
    }
}


class RequestAlreadyMatchedError(HTTPException):
    pass


class RequestAlreadyExistsError(HTTPException):
    pass
