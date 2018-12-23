import gravitate.config as config
from firebase_admin import messaging
import gravitate.data_access as data_access


def sendMessageToUser(userId, data):
    fcmToken = data_access.UserDao().get_fcm_token(userId)
    sendMessage(fcmToken, data)

def sendMessage(registration_token, data, dry_run=False):
    """ Description
        This method sends notifications to front-end. 
            Note that registration_token may not always be refreshed and 
                the operation may fail if client FCM token has changed. 

        Reference: https://firebase.google.com/docs/cloud-messaging/admin/send-messages

    :type registration_token: 
    :param registration_token: FCM token represesenting a single client device

    :type data: 
    :param data: data to send as notification

    :type dry_run:
    :param dry_run: set to True to emulate in unittests

    :raises:

    :rtype:
    """
    # This registration token comes from the client FCM SDKs.

    # See documentation on defining a message payload.
    message = messaging.Message(
        data=data,
        token=registration_token
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message, dry_run=dry_run)

    return response
