from mabel.operators import NoOpOperator, EndOperator  # type:ignore


def empty_flow(context: dict):  # pragma: no cover

    noop = NoOpOperator()
    end = EndOperator()

    flow = noop > end

    return flow
