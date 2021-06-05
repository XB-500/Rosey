from typing import Optional
from pydantic import BaseModel  # type:ignore


class CompletionSignal(BaseModel):
    work_id: str
    run_id: str
    outcome: str = "failure"


class ContinuationSignal(BaseModel):
    work_id: str
    run_id: str
    frame_id: Optional[str]
    start_point: str
    outcome: str = "partial"


class CommenceSignal(BaseModel):
    job_name: str = ""
    config: Optional[dict] = {}
