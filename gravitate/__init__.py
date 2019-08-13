# import sys
# sys.path.append('../gravitate')

import os

from flask_boiler import context
from flask_boiler import config

Config = config.Config

testing_config = Config(app_name="gravitate-dive-testing",
                        debug=True,
                        testing=True,
                        certificate_path=os.path.curdir + "/../gravitate/config_jsons/gravitate-dive-testing-firebase-adminsdk-g1ybn-2dde9daeb0.json")

CTX = context.Context
CTX.read(testing_config)
