from mabel.operators import EndOperator  # type: ignore
from mabel.operators.google import GoogleStorageStreamWriterOperator  # type: ignore
from typing import Optional


def build_flow_store_messages(context: Optional[dict] = None):

    if not context:
        context = {}

    store = GoogleStorageStreamWriterOperator(
        project=context["config"].get("target_project"),
        dataset=context["config"].get("target_dataset"),
    )
    end = EndOperator()

    flow = store > end

    return flow
