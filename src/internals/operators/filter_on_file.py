from mabel import BaseOperator  # type:ignore
from ..adapters.github import GitHubAdapter, GitHubFileModel


class FilterOnFileOperator(BaseOperator):
    def __init__(self, auth_token, organization, file_path, file_contents, **kwargs):
        super().__init__(**kwargs)
        self.AUTH_TOKEN = auth_token
        self.ORGANIZATION = organization
        self.file_path = file_path
        self.file_contents = file_contents

    def execute(self, data, context):
        THIS_REPO = data["name"]
        file = GitHubFileModel(
            file_path=self.file_path,
            owner=self.ORGANIZATION,
            repository_name=THIS_REPO,
            authentication_token=self.AUTH_TOKEN,
        )
        status, content = GitHubAdapter.get_file(file)
        content = content.decode().strip()

        if status == 200 and content == self.file_contents:
            return data, context
