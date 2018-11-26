"""
Author: Zixuan Rao
Reference: https://github.com/Amsterdam/subsidieservice/blob/master/subsidy_service/subsidy_service/config.py

Usage:
1. In testing or production, initialize Context singleton first by calling config.Context.read() in __init__.py of caller package
2. In package (data_access as an example) __init__.py, add "import config"
3. In files under the package: CTX = data_access.config.Context

"""

from google.cloud import firestore
from google.auth.transport import requests
from google.oauth2.id_token import verify_firebase_token
import logging

# [START] Firebase Admin SDK

import firebase_admin
from firebase_admin import credentials, auth

FIREBASE_CERTIFICATE_JSON_PATH = "./gravitate-e5d01-firebase-adminsdk-kq5i4-b6110cf4f0.json"

class Context():

    firebaseApp: firebase_admin.App = None
    db: firestore.Client = None
    __instance = None

    
    def __init__(self, *args, **kwargs):
        raise NotImplementedError('Do not initialize this class, use the class methods and properties instead. ')

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Context,cls).__new__(cls)
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
        cls._reloadFirebaseApp(FIREBASE_CERTIFICATE_JSON_PATH)
        cls._reloadFirestoreClient()
        return cls

    @classmethod
    def _reloadFirebaseApp(cls, certificatePath):

        try:
            cred = credentials.Certificate(certificatePath)
        except ValueError as e: 
            logging.exception('Error initializing credentials.Certificate')

        try:
            cls.firebaseApp = firebase_admin.initialize_app(cred)
        except ValueError as e:
            logging.exception('Error initializing firebaseApp')

    @classmethod
    def _reloadFirestoreClient(cls):
        try:
            cls.db = firestore.Client()
        except ValueError as e:
            logging.exception('Error initializing firestore client from cls.firebaseApp')

    
