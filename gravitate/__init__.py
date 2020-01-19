# import sys
# sys.path.append('../gravitate')

import os

from flask_boiler import context
from flask_boiler import config

Config = config.Config

testing_config = Config(app_name="gravitate-backend-testing",
                        debug=True,
                        testing=True,
                        certificate_path=os.path.curdir + "/../gravitate/config_jsons/gravitate-backend-testing-firebase-adminsdk-nztgj-d063415ecc.json")

CTX = context.Context
CTX.read(testing_config)
