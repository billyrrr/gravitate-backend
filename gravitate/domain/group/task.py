from gravitate.domain.driver_navigation.utils import get_coordinates, get_address
from gravitate.models.firestore_object import FirestoreObject
from google.cloud.firestore import Transaction, DocumentReference, DocumentSnapshot, transactional, Query

from gravitate import context

from gravitate.common import random_id

CTX = context.Context

db = CTX.db


class GroupTask:
    """
    Task queue for matching. (experimental; won't be merged for now)
        (TODO: implement and test)
    """

    @staticmethod
    @transactional
    def start_by_id(transaction: Transaction, task_id):
        ref: DocumentReference = db.collection('groupTasks').document(task_id)
        d = ref.get(ref, transaction)
        m = GroupTaskModel.from_dict(d)
        if m.in_process:
            raise ValueError("task_id: {} is already being processed. ".format(task_id))
        if m.completed:
            raise ValueError("task_id: {} is already completed. ".format(task_id))
        m.in_process = True
        transaction.set(m.to_dict())
        return m

    @staticmethod
    @transactional
    def mark_as_complete(transaction: Transaction, task_id):
        ref: DocumentReference = db.collection('groupTasks').document(task_id)
        d = ref.get(ref, transaction)
        m = GroupTaskModel.from_dict(d)
        if not m.in_process:
            raise ValueError("task_id: {} is not in process. ".format(task_id))
        if m.completed:
            raise ValueError("task_id: {} is already completed. ".format(task_id))
        m.in_process = False
        m.completed = True
        transaction.set(m.to_dict())


class GroupTaskModel(FirestoreObject):

    def __init__(self, operation_mode, ride_request_ids, in_process, completed):
        self.operation_mode = operation_mode
        self.ride_request_ids = ride_request_ids
        self.in_process = in_process
        self.completed = completed
        super().__init__()

    @staticmethod
    def from_request_json(request_form):
        operation_mode = request_form.get("operationMode", None)
        ride_request_ids = request_form.get("rideRequestIds", None)
        return GroupTaskModel(operation_mode, ride_request_ids, in_process=False, completed=False)

    @staticmethod
    def from_dict(group_task_dict):
        operation_mode = group_task_dict.get("operationMode", None)
        ride_request_ids = group_task_dict.get("rideRequestIds", None)
        in_process = group_task_dict["inProcess"]
        completed = group_task_dict["completed"]
        return GroupTaskModel(operation_mode, ride_request_ids, in_process=in_process, completed=completed)

    def to_dict(self) -> dict:
        return {
            "operationMode": self.operation_mode,
            "rideRequestIds": self.ride_request_ids,
            "inProcess": self.in_process,
            "completed": self.completed
        }
