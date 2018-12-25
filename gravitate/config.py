class GravitateConfig:
    DEBUG = None
    FIREBASE_CERTIFICATE_JSON_PATH = None
    APP_NAME = None


class DevelopmentGravitateConfig(GravitateConfig):
    DEBUG = True
    FIREBASE_CERTIFICATE_JSON_PATH = "gravitate/gravitate-dev-firebase-adminsdk-79k5b-04b4ed676d.json"
    APP_NAME = "gravitate-dev"


class StagingGravitateConfig(GravitateConfig):
    FIREBASE_CERTIFICATE_JSON_PATH = "gravitate/gravitate-e5d01-firebase-adminsdk-kq5i4-943fb267ce.json"
    APP_NAME = "gravitate-e5d01"