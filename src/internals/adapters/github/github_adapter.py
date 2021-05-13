import base64
import requests
import ujson as json
from enum import Enum
from pydantic import BaseModel



class GitHubGroup(str, Enum):
    users = 'users'
    orgs = 'orgs'

class GitHubPushFileModel(BaseModel):
    file_name: str
    repository_name: str
    branch_name: str
    auth_token: str

class GitHubListReposModel(BaseModel):
    classification: GitHubGroup = GitHubGroup.users
    name: str
    auth_token: str


class GitHubAdapter():

    @staticmethod
    def push_file(file_model: GitHubPushFileModel):
        url = F"https://api.github.com/repos/{file_model.repository_name}/contents/{file_model.file_name}"
        base64content=base64.b64encode(open(file_model.file_name,"rb").read())
        data = requests.get(
                url + '?ref=' + file_model.branch_name, 
                headers={"Authorization": "token "+ file_model.authentication_token}).json()
        sha = data['sha']
        if base64content.decode('utf-8')+"\n" != data['content']:
            message = json.dumps({"message":"update",
                                "branch": file_model.branch_name,
                                "content": base64content.decode("utf-8") ,
                                "sha": sha
                                })
            resp = requests.put(
                    url,
                    data=message,
                    headers={"Content-Type": "application/json", "Authorization": "token " + file_model.authentication_token})
            return resp
        else:
            return False


    def list_repos(repos: GitHubListReposModel):
        apiurl = F'https://api.github.com/{repos.classification}/{repos.name}/repos'
        response = requests.get(apiurl, auth=('access_token', repos.auth_token))
        return response


    def get_file(urk, auth_token):
        git_name = row['name']
        url = (giturl + git_name + git_tail)
        response = requests.get(url, auth=('access_token', access_token))
        data = response.text

        return data