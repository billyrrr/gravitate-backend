class BaseRideRequestServiceException(Exception):
    def __init__(self, message=''):
        self.message = message

class EventNotFoundException(BaseRideRequestServiceException):
    pass

