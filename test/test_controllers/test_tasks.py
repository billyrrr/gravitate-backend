from google.cloud import tasks_v2
from unittest import TestCase
from gravitate.context import Context as CTX
from gravitate.common import random_id

# Configs for task queue
# Run "gcloud beta tasks queues describe my-appengine-queue" to obtain them

project_name = CTX.firebaseApp.name
queue_region = 'us-central1'


class CloudTasksTest(TestCase):
    """ Tests that tasks_v2 is configured

    ref: https://googleapis.github.io/google-cloud-python/latest/tasks/gapic/v2/api.html
    """

    def setUp(self):
        self.queue_name = "test-my-appengine-queue-" + random_id()[:5]  # Use first 5 digits of random id only
        self.tasks_client = tasks_v2.CloudTasksClient()
        parent = self.tasks_client.location_path('gravitate-dive-testing', 'us-central1')
        queue = {
            # The fully qualified path to the queue
            'name':  str(self.tasks_client.queue_path(project_name, queue_region, self.queue_name))
        }
        response = self.tasks_client.create_queue(parent, queue)

    def tearDown(self):
        name = self.tasks_client.queue_path(project_name, queue_region, self.queue_name)
        self.tasks_client.delete_queue(name)

    def test_create_queue(self):
        """
        "WARNING: Using this method may have unintended side effects if you are using an App Engine queue.yaml or
            queue.xml file to manage your queues. Read Overview of Queue Management and queue.yaml before using this
            method."

        :return:
        """

        parent = self.tasks_client.queue_path('gravitate-dive-testing', 'us-central1', self.queue_name)
        print(parent)
        task = {
            'app_engine_http_request': {  # Specify the type of request.
                'http_method': 'POST',
                'relative_uri': '/example_task_handler'
            }
        }
        response = self.tasks_client.create_task(parent, task)
        print(response)
