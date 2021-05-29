"""
These signals are the API interfaces for the controller, they define the fields which
are part of the interface.
"""
from typing import Optional
from pydantic import BaseModel  # type:ignore


class CompletionSignal(BaseModel):
    """
    When work is complete, it sends a 'completion' signal to the controller for the
    controller to mark the work as complete and kick off any follow-up work.
    """
    work_id: str
    run_id: str
    outcome: str = "failure"

class ContinuationSignal(BaseModel):
    """
    When work cannot be completed by one worker, it sends a 'continuation' signal to
    the controller for it to kick off another worker to continue processing the task.
    """
    work_id: str
    run_id: str
    frame_id: Optional[str]
    start_point: str
    outcome: str = "partial"

class CommenceSignal(BaseModel):
    """
    To start a pipeline, an external service (such as cloud scheduler) sends a
    'commence' signal to the controller for it to initiate the workers to execute the
    tasks which make up the pipeline.
    """
    job_name: str = ''
    config: Optional[dict] = {}