from mabel import BaseOperator  # type:ignore
from ..adapters.github import GitHubAdapter, GitHubListReposModel, GitHubGroup


class GetReposOperator(BaseOperator):
    def __init__(self, auth_token, organization, **kwargs):

        super().__init__(**kwargs)

        self.AUTH_TOKEN = auth_token
        self.ORGANIZATION = organization

    def execute(self, data, context):

        repos = GitHubListReposModel(
            authentication_token=self.AUTH_TOKEN,
            name=self.ORGANIZATION,
            classification=GitHubGroup.orgs,
        )

        repo_list = GitHubAdapter.list_repos(repos).json()
        self.logger.debug(f"I found {len(repo_list)} repositories.")

        for repo in repo_list:
            yield repo, context
