from mabel.operators import EndOperator
from internals.operators.get_repos_operator import GetReposOperator  # type:ignore


from mabel import operator
@operator
def print_item(data):
    print(data)
    return data

def sync_repos_flow(context):

    get_repos = GetReposOperator(
        auth_token=context['GITHUB_TOKEN'],
        organization=context['GITHUB_ORG']
    )
    end = EndOperator()

    flow = get_repos > print_item > end

    return flow