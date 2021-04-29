from mabel.operators import EndOperator
from mabel.operators.google import GoogleStorageBatchWriterOperator
from typing import Optional


def build_flow_store_messages(context: Optional[dict] = None):

    if not context:
        context = {}

    store = GoogleStorageBatchWriterOperator(
            project=context['config'].get('target_project'),
            dataset=context['config'].get('target_dataset')
        )
    end = EndOperator()

    flow = store > end

    return flow
