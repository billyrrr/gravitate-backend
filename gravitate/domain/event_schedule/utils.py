import warnings

from gravitate.data_access import UserDao
from gravitate.domain.orbit import Orbit
from . import CTX


def getMemberProfilePhotoUrls(orbit: Orbit) -> [str]:
    """ Description
        [Assigned to Leon]
        Don't have to follow the method signature, but the signature is required to get other code working.
        Orbits can be obtained through any other ways, and buildEventSchedule can be called from elsewhere.

    :raises:

    :rtype:
    """
    # Must go through each userTicketPair (key = userIDs)
    photo_urls = []
    if CTX.testing:
        warnings.warn("Using testing mode, skipping member profile photo urls evaluation. ")
        return photo_urls

    for uid in orbit.user_ticket_pairs:
        user = UserDao().get_user_by_id(uid)
        photo_url = user.photo_url
        photo_urls.append(photo_url)

    return photo_urls
