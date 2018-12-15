from gravitate.models import User

import string
import gravitate.config as config

auth = config.auth

def update_user(user:User):
    auth.update_user(user.uid,
    phone_number = user.phone_number,
    display_name  = user.display_name,
    photo_url  = user.photo_url,
    disabled = False, app = config.Context.firebaseApp)

# TODO: firebase_admin auth