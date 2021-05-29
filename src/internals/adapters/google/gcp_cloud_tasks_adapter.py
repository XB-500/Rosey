"""
Google Cloud Platform: CloudTasks Adapter

An interface to CloudTasks on GCP to assist with performing common
functionality with this component.

Derived from the examples on:
    https://github.com/googleapis/python-tasks

Requirements
    google-cloud-tasks
    pydantic
"""
import os
try:
    from google.cloud import tasks_v2  # type: ignore
    from google.protobuf import timestamp_pb2  # type: ignore
except ImportError:
    tasks_v2 = None  # type:ignore
import datetime
from mabel.logging import get_logger  # type: ignore
from mabel.data.formats.json import serialize  # type: ignore
from pydantic import BaseModel  # type:ignore
from typing import Optional, Union
from ...errors import MissingDependencyError


# The models are pydantic data models:
# https://pydantic-docs.helpmanual.io/usage/models/
# The models inherit from each other in turn, adding more fields as they go.
class CloudTasksQueueLocationModel(BaseModel):
    project: str = "mabeldev"
    location: str = "europe-west2"


class CloudTasksQueueModel(CloudTasksQueueLocationModel):
    queue_name: str


class CloudTasksTaskModel(CloudTasksQueueModel):
    """
    Cloud Tasks Task Model

    Parameters:
        project: string
        location: string
        queue_name: string
        target_url: string
        payload: dictionary or string (optional)
        in_seconds: integer (optional)
        task_name: string (optional)
    """
    target_url: str
    payload: Optional[Union[str, dict]]
    in_seconds: Optional[int] = None
    task_name: Optional[str] = None

class CompletionModel(CloudTasksTaskModel):
    queue_name = "complete"
    target_url = "<host>/complete"

class ContinuationModel(CloudTasksTaskModel):
    queue_name = "continue"
    target_url = "<host>/continue"

class CloudTasksAdapter:

    @staticmethod
    def _stubbed_create_task(task: CloudTasksTaskModel):
        print(task.json())
        return None

    @staticmethod
    def create_task(task: CloudTasksTaskModel):
        """
        Create a task for a given queue with an arbitrary payload.

        Paramters:
            task: CloudTasksTaskModel (or CompletionSignal)
                The details of the request

        Returns:
            Task Object

        Raises:
            MissingDependencyError
                When google.cloud.tasks_v2 isn't available
        """
        # if the environment variables are set to stub cloud tasks,
        # output to the console instead of sending to cloud tasks
        if os.environ.get("STUB_CLOUD_TASKS", False):
            return CloudTasksAdapter._stubbed_create_task(task)

        if not tasks_v2:
            raise MissingDependencyError("`google.cloud.tasks_v2` must be installed")

        client = tasks_v2.CloudTasksClient()

        # Construct the fully qualified queue name.
        parent = client.queue_path(task.project, task.location, task.queue_name)

        # Construct the request body.
        cloud_task = {
            "http_request": {  # Specify the type of request.
                "http_method": tasks_v2.HttpMethod.POST,
                "url": task.target_url,  # The full url path that the task will be sent to.
            }
        }
        if task.payload is not None:
            if isinstance(task.payload, dict):
                payload = serialize(task.payload)
                cloud_task["http_request"]["headers"] = {
                    "Content-type": "application/json"
                }

            # The API expects a payload of type bytes.
            cloud_task["http_request"]["body"] = payload.encode()

        if task.in_seconds is not None:
            # Convert "seconds from now" into an rfc3339 datetime string.
            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=task.in_seconds)

            # Create Timestamp protobuf.
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)

            # Add the timestamp to the tasks.
            cloud_task["schedule_time"] = timestamp  # type:ignore

        if task.task_name is not None:
            # Add the name to tasks.
            cloud_task["name"] = f"{parent}/tasks/{task.task_name}"  # type:ignore

        # Use the client to build and send the task.
        response = client.create_task(request={"parent": parent, "task": cloud_task})  # type:ignore
        get_logger().debug(f"CloudTasks task created: {response.name}")
        return response

    @staticmethod
    def create_queue(queue: CloudTasksQueueModel):
        """
        Create a task queue.

        Paramters:
            queue: CloudTasksQueueModel
                The details of the request

        Returns:
            Queue Object
        """
        client = tasks_v2.CloudTasksClient()
        # Construct the fully qualified location path.
        parent = f"projects/{queue.project}/locations/{queue.location}"
        # Construct the create queue request.
        task_queue = {
            "name": client.queue_path(queue.project, queue.location, queue.queue_name)
        }
        # Use the client to create the queue.
        response = client.create_queue(request={"parent": parent, "queue": task_queue})  # type:ignore
        return response

    @staticmethod
    def list_queues(location: CloudTasksQueueLocationModel):
        """
        List all task queues.

        Paramters:
            location: CloudTasksQueueLocationModel
                The details of the request

        Yields:
            Queue Object
        """
        client = tasks_v2.CloudTasksClient()
        # Construct the fully qualified location path.
        parent = f"projects/{location.project}/locations/{location.location}"
        # Use the client to obtain the queues.
        yield from client.list_queues(request={"parent": parent})  # type:ignore

    @staticmethod
    def list_queued_tasks(queue: CloudTasksQueueModel):
        """
        Retreive the tasks from a queue.

        Paramters:
            queue: CloudTasksQueue

        Yields:
            task
        """
        from google.cloud import tasks_v2beta3

        client = tasks_v2beta3.CloudTasksClient()

        # Construct the fully qualified queue name.
        parent = client.queue_path(queue.project, queue.location, queue.queue_name)

        # Iterate over all results
        yield from client.list_tasks(request={"parent": parent})  # type:ignore
