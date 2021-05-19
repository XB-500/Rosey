import base64
import requests
import ujson as json
from enum import Enum
from pydantic import BaseModel
from typing import Optional



class GitHubGroup(str, Enum):
    users = 'users'
    orgs = 'orgs'

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

class GitHubAdapter():

    @staticmethod
    def push_file(file_model: GitHubFileModel):
        url = F"https://api.github.com/repos/{file_model.owner}/{file_model.repository_name}/contents/{file_model.file_path}"

        payload = {}
        payload["path"] = file_model.file_path
        payload["branch"] = file_model.branch_name
        payload["message"] = "Synchronising with Template"
        payload["content"] = base64.b64encode(file_model.contents).decode()

        resp = requests.put(
                url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json", "Authorization": "token " + file_model.authentication_token})

        print(resp)

        return resp


    @staticmethod
    def list_repos(repos: GitHubListReposModel):
        apiurl = F'https://api.github.com/{repos.classification}/{repos.name}/repos'
        response = requests.get(apiurl, auth=('access_token', repos.authentication_token))
        return response

    @staticmethod
    def get_file(file_model: GitHubFileModel):
        url = f"https://api.github.com/repos/{file_model.owner}/{file_model.repository_name}/contents/{file_model.file_path}"
        response = requests.get(url, auth=('access_token', file_model.authentication_token))
        if response.status_code == 200:
            return response.status_code, base64.b64decode(response.json().get('content', b''))
        return response.status_code, b''

    @staticmethod
    def get_heads():
        OWNER = "mabel-dev"
        REPO = "mabel"
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/git/refs/heads"
        response = requests.get(url)
        print(response.json())

if __name__ == "__main__":
    GitHubAdapter.get_heads()