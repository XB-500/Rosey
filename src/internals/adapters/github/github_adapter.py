import base64
import requests
import ujson as json
from enum import Enum
from pydantic import BaseModel  # type:ignore
from typing import Optional


class GitHubGroup(str, Enum):
    users = "users"
    orgs = "orgs"


class GitHubFileModel(BaseModel):
    file_path: str
    owner: str
    repository_name: str
    branch_name: Optional[str]
    authentication_token: str
    contents: Optional[bytes]


class GitHubListReposModel(BaseModel):
    classification: GitHubGroup = GitHubGroup.users
    name: str
    authentication_token: str


class GitHubAdapter:
    @staticmethod
    def push_file(file_model: GitHubFileModel):
        file_model.file_path = file_model.file_path.replace("\\", "/")
        url = f"https://api.github.com/repos/{file_model.owner}/{file_model.repository_name}/contents/{file_model.file_path}"

        payload = {}
        payload["path"] = file_model.file_path
        payload["branch"] = file_model.branch_name  # type:ignore
        payload["message"] = "Synchronising with Template"
        payload["content"] = base64.b64encode(
            file_model.contents
        ).decode()  # type:ignore

        resp = requests.put(
            url,
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "Authorization": "token " + file_model.authentication_token,
            },
        )
        return resp

    @staticmethod
    def list_repos(repos: GitHubListReposModel):
        apiurl = f"https://api.github.com/{repos.classification}/{repos.name}/repos"
        response = requests.get(
            apiurl, auth=("access_token", repos.authentication_token)
        )
        return response

    @staticmethod
    def get_file(file_model: GitHubFileModel):
        url = f"https://api.github.com/repos/{file_model.owner}/{file_model.repository_name}/contents/{file_model.file_path}"
        response = requests.get(
            url, auth=("access_token", file_model.authentication_token)
        )
        if response.status_code == 200:
            return response.status_code, base64.b64decode(
                response.json().get("content", b"")
            )
        return response.status_code, b""

    @staticmethod
    def get_branches(owner: str, repository_name: str, authentication_token: str):
        url = f"https://api.github.com/repos/{owner}/{repository_name}/git/refs/heads"
        response = requests.get(url, auth=("access_token", authentication_token))
        return response.json()

    @staticmethod
    def create_branch(  # nosec - no hardcoded password
        owner: str,
        repository_name: str,
        branch_from: str = "main",
        branch_name: str = "branch",
        authentication_token: str = "",
    ):

        branches = GitHubAdapter.get_branches(
            owner, repository_name, authentication_token
        )
        sha = [
            branch["object"]["sha"]
            for branch in branches
            if branch["ref"] == f"refs/heads/{branch_from}"
        ].pop()
        url = f"https://api.github.com/repos/{owner}/{repository_name}/git/refs"
        data = {"ref": f"refs/heads/{branch_name}", "sha": sha}
        response = requests.post(
            url, data=json.dumps(data), auth=("access_token", authentication_token)
        )
        print(response.status_code, response.text)
        return True

    @staticmethod
    def submit_pr(
        owner: str,
        repository_name: str,
        branch_name: str = "",
        target_branch: str = "main",
        title: str = "",
        authentication_token: str = "",
    ):
        url = f"https://api.github.com/repos/{owner}/{repository_name}/pulls"
        data = {"head": branch_name, "base": target_branch, "title": title}
        response = requests.post(
            url, data=json.dumps(data), auth=("access_token", authentication_token)
        )
        return response.status_code % 100 == 2
