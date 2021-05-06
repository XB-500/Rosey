import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../src'))
sys.path.insert(1, os.path.join(sys.path[0], 'src'))
from internals.adapters.google import CloudTasksAdapter, CloudTasksTaskModel


def test_cloud_tasks_stub():
    """ make sure CT stubbing works """
    os.environ['STUB_CLOUD_TASKS'] = "True"

    task = CloudTasksAdapter.create_task(
        CloudTasksTaskModel(
            project='project',
            queue_name='queue',
            target_url='url'
        )
    )


if __name__ == "__main__":
    test_cloud_tasks_stub()

    print("all tests complete")