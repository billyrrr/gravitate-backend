from models import User

import string
from firebase_admin import auth

def update_user(user:User):
    auth.update_user(user.uid,
    phone_number = user.phone_number,
    display_name  = user.display_name,
    photo_url  = user.photo_url,
    disabled = False)