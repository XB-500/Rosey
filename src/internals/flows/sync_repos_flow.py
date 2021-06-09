from re import A
from mabel.operators import EndOperator
from ..operators import (
    GetReposOperator,
    FilterOnFileOperator,
    SyncWithRepoOperator,
)  # type:ignore


from mabel import operator


@operator
def print_item(data):
    print(data)
    return data


def sync_repos_flow(context):

    COMMENTS = (
        open("comments.txt")
        .read()
        .replace(
            "{TEMPLATE_REPO}",
            f"https://github.com/{context['GITHUB_ORG']}/{context['TEMPLATE_REPO']}",
        )
    )

    get_all_repos = GetReposOperator(
        auth_token=context["GITHUB_TOKEN"], organization=context["GITHUB_ORG"]
    )
    filter_based_on_template = FilterOnFileOperator(
        auth_token=context["GITHUB_TOKEN"],
        organization=context["GITHUB_ORG"],
        file_path="TEMPLATE",
        file_contents=f"https://github.com/{context['GITHUB_ORG']}/{context['TEMPLATE_REPO']}",
    )
    sync = SyncWithRepoOperator(
        auth_token=context["GITHUB_TOKEN"],
        organization=context["GITHUB_ORG"],
        source_repo=context["TEMPLATE_REPO"],
        comments=COMMENTS,
    )

    end = EndOperator()

    flow = get_all_repos >> filter_based_on_template >> sync >> end

    return flow
