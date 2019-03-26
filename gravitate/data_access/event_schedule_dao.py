"""Author: David Nong
"""

from typing import Type

import google
from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot

from gravitate import context
from gravitate.domain.event_schedule import AirportEventSchedule

CTX = context.Context

db = CTX.db


class EventScheduleGenericDao:
    """ Description	
        Database access object for eventSchedules
    """

    def __init__(self, userId=None, userRef=None):
        """ Description
            Either userId or userRef must be specified

            :type self:
            :param self:

            :type userId:
            :param userId:

            :type userRef:
            :param userRef:

            :raises:

            :rtype:
        """

        assert (userId != None) or (userRef != None), \
            "Both userId and userRef are None"
        assert (userId == None) or (userRef == None), \
            "Receiving both userId: {} and userRef: {}".format(userId, userRef)

        if userId:
            self.eventScheduleCollectionRef = db.collection('users').document(userId).collection('eventSchedules')
        else:
            self.eventScheduleCollectionRef = userRef.collection('eventSchedules')

    def get_with_transaction(self, transaction: Transaction, eventScheduleRef: DocumentReference) \
            -> Type[AirportEventSchedule]:
        """ Description
            Note that this cannot take place if transaction already received write operations. 
            "If a transaction is used and it already has write operations added, this method cannot be used
                (i.e. read-after-write is not allowed)."

        :type self:
        :param self:

        :type transaction:Transaction:
        :param transaction:Transaction:

        :type eventScheduleRef:DocumentReference:
        :param eventScheduleRef:DocumentReference:

        :raises:

        :rtype:
        """

        try:
            snapshot: DocumentSnapshot = eventScheduleRef.get(
                transaction=transaction)
            snapshotDict: dict = snapshot.to_dict()
            eventSchedule = AirportEventSchedule.from_dict(snapshotDict)
            return eventSchedule

        except google.cloud.exceptions.NotFound:
            raise Exception('No such document! ' + str(eventScheduleRef.id))

    def get(self, eventScheduleRef: DocumentReference):
        transaction = db.transaction()
        eventScheduleResult = self.get_with_transaction(
            transaction, eventScheduleRef)
        transaction.commit()
        return eventScheduleResult

    def create(self, eventSchedule: Type[AirportEventSchedule]) -> DocumentReference:
        """ Description
        :type self:
        :param self:

        :type eventSchedule
        :Type[AirportEventSchedule]:


        :raises:

        :rtype:
        """
        # TODO fix
        # TODO fix by changing to .add()
        _, eventScheduleRef = self.eventScheduleCollectionRef.a(eventSchedule.to_dict())
        return eventScheduleRef

    def delete(self, singleEventScheduleRef: DocumentReference):
        """ Description
            This function deletes a ride request from the database

        :type self:
        :param self:

        :type singleEventScheduleRef:DocumentReference:
        :param singleEventScheduleRef:DocumentReference:

        :raises:

        :rtype:
        """
        return singleEventScheduleRef.delete()

    def delete_event_by_id(self, eventId: str):
        """ Description
            This function deletes an event from EventSchedules
        """
        self.eventScheduleCollectionRef.document(eventId).delete()

    @staticmethod
    def set_with_transaction(transaction: Transaction, newEventSchedule: Type[AirportEventSchedule],
                             eventScheduleRef: DocumentReference):
        """ Description
            Note that a read action must have taken place before anything is set with that transaction. 

        :type self:
        :param self:

        :type transaction:Transaction:
        :param transaction:Transaction:

        :type newEventSchedule:Type[AirportEventSchedule]:
        :param newEventSchedule:Type[AirportEventSchedule]:

        :type eventScheduleRef:DocumentReference:
        :param eventScheduleRef:DocumentReference:

        :raises:

        :rtype:
        """
        return transaction.set(eventScheduleRef, newEventSchedule)
