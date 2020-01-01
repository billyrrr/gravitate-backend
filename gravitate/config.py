"""
Author: Zixuan Rao
Reference:
    http://flask.pocoo.org/docs/1.0/config/
    https://medium.freecodecamp.org/structuring-a-flask-restplus-web-service-for-production-builds-c2ec676de563
"""

import os

gravitate_module_path = os.path.dirname(__file__)  # should be equivalent to "../gravitate"
config_jsons_path = os.path.join(gravitate_module_path, "config_jsons")


class GravitateConfig:
    """
    TESTING: (authenticate decorator will return uid as the value of header["Authentication"])
        Enable testing mode. Exceptions are propagated rather than handled by the the app’s error handlers.
        Extensions may also change their behavior to facilitate easier testing.
        You should enable this in your own tests.
    DEBUG:
        Whether debug mode is enabled.
        When using flask run to start the development server, an interactive debugger will be shown for unhandled
        exceptions, and the server will be reloaded when code changes. The debug attribute maps to this config key.
        This is enabled when ENV is 'development' and is overridden by the FLASK_DEBUG environment variable.
        It may not behave as expected if set in code.

    Note that this Config currently does not affect (Flask) main.app CONFIG.
    TODO: extend from Flask Config and apply to main.app

    """
    DEBUG = None
    TESTING = None
    FIREBASE_CERTIFICATE_JSON_PATH = None
    APP_NAME = None


class DevelopmentGravitateConfig(GravitateConfig):
    DEBUG = True
    TESTING = False
    FIREBASE_CERTIFICATE_JSON_PATH = os.path.join(config_jsons_path,
                                                  "gravitate-dive-dev-5ccd85db04e7.json")
    APP_NAME = "gravitate-dive-dev"


class TestingGravitateConfig(GravitateConfig):
    DEBUG = True
    TESTING = True
    FIREBASE_CERTIFICATE_JSON_PATH = os.path.join(config_jsons_path,
                                                  "gravitate-backend-testing-firebase-adminsdk-nztgj-d063415ecc.json")
    APP_NAME = "gravitate-backend-testing"


class StagingGravitateConfig(GravitateConfig):
    pass
    # FIREBASE_CERTIFICATE_JSON_PATH = os.path.join(config_jsons_path,
    #                                               "gravitate-e5d01-firebase-adminsdk-kq5i4-943fb267ce.json")
    # APP_NAME = "gravitate-e5d01"
    # DEBUG = False
    # TESTING = False
