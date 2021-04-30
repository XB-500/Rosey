# https://github.com/googleapis/python-tasks


from google.cloud import tasks_v2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from mabel.logging import get_logger  # type: ignore
from mabel.formats.json import serialize  # type: ignore
import datetime


from pydantic import BaseModel
from typing import Optional, Union


class CloudTasksModel(BaseModel):
    project: str
    queue_name: str
    location: str = 'europe'
    target_url: str = 'http:s//abc.com/a'
    payload: Optional[Union[str,dict]]
    in_seconds: Optional[int] = None
    task_name: Optional[str] = None

class CompletionSignal(CloudTasksModel):
    pass


class CloudTasksAdapter():

    @staticmethod
    def create_http_task(task: CloudTasksModel):
        """
        Create a task for a given queue with an arbitrary payload.

        Paramters:
            task: CloudTasksModel (or CompletionSignal)
                The details of the request

        Returns:
            Response Object
        """
        client = tasks_v2.CloudTasksClient()

        # Construct the fully qualified queue name.
        parent = client.queue_path(
                task.project,
                task.location,
                task.queue_name)

        # Construct the request body.
        cloud_task = {
            "http_request": {  # Specify the type of request.
                "http_method": tasks_v2.HttpMethod.POST,
                "url": task.target_url,  # The full url path that the task will be sent to.
            }
        }
        if task.payload is not None:
            if isinstance(task.payload, dict):
                payload = serialize(payload)
                cloud_task["http_request"]["headers"] = {"Content-type": "application/json"}

            # The API expects a payload of type bytes.
            cloud_task["http_request"]["body"] = payload.encode()

        if task.in_seconds is not None:
            # Convert "seconds from now" into an rfc3339 datetime string.
            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=task.in_seconds)

            # Create Timestamp protobuf.
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)

            # Add the timestamp to the tasks.
            cloud_task["schedule_time"] = timestamp

        if task.task_name is not None:
            # Add the name to tasks.
            cloud_task["name"] = task.task_name

        # Use the client to build and send the task.
        response = client.create_task(request={"parent": parent, "task": cloud_task})
        get_logger.debug("CloudTasks task created: {response.name}")
        return response


    @staticmethod
    def create_queue(project, queue_name, location):
        """
        Create a task queue.
        """
        client = tasks_v2.CloudTasksClient()

        # Construct the fully qualified location path.
        parent = f"projects/{project}/locations/{location}"

        # Construct the create queue request.
        queue = {"name": client.queue_path(project, location, queue_name)}

        # Use the client to create the queue.
        response = client.create_queue(request={"parent": parent, "queue": queue})

        print("Created queue {}".format(response.name))
        return response


    @staticmethod
    def list_queues(project, location):
        """
        List all task queues.
        """
        client = tasks_v2.CloudTasksClient()

        # Construct the fully qualified location path.
        parent = f"projects/{project}/locations/{location}"

        # Use the client to obtain the queues.
        response = client.list_queues(request={"parent": parent})

        # Print the results.
        num_results = 0
        for queue in response:
            num_results = num_results + 1
            print(queue.name)

        if num_results == 0:
            print("No queues found!")


    @staticmethod
    def queue_length():
        client = tasks_v2.CloudTasksClient()

        # Construct the fully qualified queue name.
        parent = client.queue_path(
                task.project,
                task.location,
                task.queue_name)

        # Iterate over all results
        for element in client.list_tasks(parent):
            # process element
            pass

        # Iterate over results one page at a time
        for page in client.list_tasks(parent).pages:
            for element in page:
                # process element
                pass