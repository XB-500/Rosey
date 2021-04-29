from mabel.operators import EndOperator
from mabel.operators.google import GoogleStorageBatchWriterOperator
from typing import Optional


def build_flow_store_messages(config: Optional[dict] = None):

    if not config:
        config = {}

    store = GoogleStorageBatchWriterOperator(
            project=config.get('target_project'),
            dataset=config.get('target_dataset')
        )
    end = EndOperator()

    flow = store > end

    return flow
