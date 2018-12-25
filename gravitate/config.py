"""
Author: Zixuan Rao
Reference:
    http://flask.pocoo.org/docs/1.0/config/
    https://medium.freecodecamp.org/structuring-a-flask-restplus-web-service-for-production-builds-c2ec676de563
"""


class GravitateConfig:
    """
    TESTING: (authenticate decorator will return uid as "testuid1")
        Enable testing mode. Exceptions are propagated rather than handled by the the app’s error handlers.
        Extensions may also change their behavior to facilitate easier testing.
        You should enable this in your own tests.
    DEBUG:
        Whether debug mode is enabled.
        When using flask run to start the development server, an interactive debugger will be shown for unhandled
        exceptions, and the server will be reloaded when code changes. The debug attribute maps to this config key.
        This is enabled when ENV is 'development' and is overridden by the FLASK_DEBUG environment variable.
        It may not behave as expected if set in code.

    """
    DEBUG = None
    TESTING = None
    FIREBASE_CERTIFICATE_JSON_PATH = None
    APP_NAME = None


class DevelopmentGravitateConfig(GravitateConfig):
    DEBUG = True
    TESTING = False
    FIREBASE_CERTIFICATE_JSON_PATH = "gravitate/gravitate-dev-firebase-adminsdk-79k5b-04b4ed676d.json"
    APP_NAME = "gravitate-dev"


class TestingGravitateConfig(GravitateConfig):
    DEBUG = True
    TESTING = True
    FIREBASE_CERTIFICATE_JSON_PATH = "gravitate/gravitate-dev-firebase-adminsdk-79k5b-04b4ed676d.json"
    APP_NAME = "gravitate-dev"


class StagingGravitateConfig(GravitateConfig):
    FIREBASE_CERTIFICATE_JSON_PATH = "gravitate/gravitate-e5d01-firebase-adminsdk-kq5i4-943fb267ce.json"
    APP_NAME = "gravitate-e5d01"
    DEBUG = False
    TESTING = False
