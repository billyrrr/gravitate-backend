"""
Author: Zixuan Rao
Reference: https://github.com/Amsterdam/subsidieservice/blob/master/subsidy_service/subsidy_service/context.py

Usage:
1. In testing or production, initialize Context singleton first by calling config.Context.read() in __init__.py of
    caller package
2. In package (test_data_access as an example) __init__.py, add "import config"
3. In files under the package: CTX = test_data_access.config.Context

"""

from google.cloud import firestore
import logging

# [START] Firebase Admin SDK

import firebase_admin
from firebase_admin import credentials, auth

#
# # Original Firebase set-up certs
#
import gravitate.config as gravitate_config

config = gravitate_config.TestingGravitateConfig


# New project-id: gravitate-dev certs
# Note that "../gravitate/*" works by trial and error so that the path works both at "/gravitate" and "/test"
# TODO improve import


class Context():
    firebaseApp: firebase_admin.App = None
    db: firestore.Client = None
    debug = None
    testing = None
    _cred = None
    __instance = None

    def __init__(self, *args, **kwargs):
        raise NotImplementedError('Do not initialize this class, use the class methods and properties instead. ')

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Context, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    @classmethod
    def read(cls):
        """ Description
            Read config file andd reload firebase app and firestore client. 

            # TODO read config from *.ini file (not provided yet)

        :type cls:
        :param cls:

        :raises:

        :rtype:
        """
        cls._reloadDebugFlag(config.DEBUG)
        cls._reloadTestingFlag(config.TESTING)
        cls._reloadFirebaseApp(config.FIREBASE_CERTIFICATE_JSON_PATH)
        cls._reloadFirestoreClient(config.FIREBASE_CERTIFICATE_JSON_PATH)
        return cls

    @classmethod
    def _reloadDebugFlag(cls, debug):
        cls.debug = debug

    @classmethod
    def _reloadTestingFlag(cls, testing):
        """
        When testing is set to True, all authenticate decorators in services returns uid as "testuid1"
        :param testing:
        :return:
        """
        cls.testing = testing

    @classmethod
    def _reloadFirebaseApp(cls, certificatePath):

        try:
            cls._cred = credentials.Certificate(certificatePath)
        except ValueError as e:
            logging.exception('Error initializing credentials.Certificate')
        # TODO delete certificate path in function call

        try:
            cls.firebaseApp = firebase_admin.initialize_app(credential=cls._cred, name=config.APP_NAME)
        except ValueError as e:
            logging.exception('Error initializing firebaseApp')

    @classmethod
    def _reloadFirestoreClient(cls, credPath):
        try:
            cls.db = firestore.Client.from_service_account_json(credPath)
        except ValueError as e:
            logging.exception('Error initializing firestore client from cls.firebaseApp')
