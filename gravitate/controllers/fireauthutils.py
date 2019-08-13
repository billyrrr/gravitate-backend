from firebase_admin import auth

import gravitate.context as config
from gravitate.domain.user.models import User


# auth = config.auth


def update_user(user: User):
    auth.update_user(user.uid,
                     phone_number=user.phone_number,
                     display_name=user.display_name,
                     photo_url=user.photo_url,
                     disabled=False, app=config.Context.firebase_app)

# TODO: firebase_admin auth
