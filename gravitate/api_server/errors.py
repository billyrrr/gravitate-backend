from flask_restful import HTTPException

errors = {
    'RequestAlreadyMatchedError': {
        "message": "Ride request has requestCompletion as True. Un-match from an orbit first. ",
        "status": 500
    },
    'RequestAlreadyExistsError': {
        "message": "Ride request on the same day (or for the same event) already exists",
        "status": 400
    },
    'EventNotFoundError': {
        "message": "invalid airport code and datetime combination or error finding airport location in backend",
        "status": 400
    },
    'RequestNotMatchedError': {
        "message": "Trying to un-match a ride request that is not matched to an orbit yet. ",
        "status": 400
    }

}


class RequestAlreadyMatchedError(HTTPException):
    pass


class RequestAlreadyExistsError(HTTPException):
    pass


class RequestNotMatchedError(HTTPException):
    pass
