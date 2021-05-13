import os
import uvicorn    # type: ignore
from internals.flows.store_message_flow import build_flow_store_messages
from fastapi import FastAPI, HTTPException  # type:ignore
from fastapi.responses import UJSONResponse  # type:ignore
from fastapi import Request
from mabel.logging import get_logger, set_log_name    # type: ignore
from mabel.data.formats import json    # type: ignore
from mabel.utils.common import build_context    # type: ignore


set_log_name("ROSEY")
logger = get_logger()

app = FastAPI()

context = build_context()


@app.get("/test")
async def receive_test_request(repo: str):
    request_id = -1
    try:
        json_object = await request.json()
        request_id = abs(hash(json.serialize(json_object)))

        # download repo
        # run pytest
        # if errors, raise issues

    except Exception as err:
        error_message = F"{type(err).__name__}: {err} (ID:{request_id})"
        logger.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)
    finally:
        logger.debug(F"Finished ID:{request_id}")

    return "okay"


@app.post("/hook")
async def receive_web_hook(request: Request):

    request_id = -1
    
    try:

        json_object = await request.json()

        request_id = abs(hash(json.serialize(json_object)))
        
        github_event = request.headers.get("X-Github-Event")
        logger.debug(F"Started ID: {request_id} - {github_event}")

        # default message
        message = f"Unhandled Event Received `{github_event}`"

        # run the flow to store the payloads
        with build_flow_store_messages(context) as runner:
            runner(json_object)

        if github_event == 'push': #

            submitter_email = json_object.get('pusher', {}).get('email', {})
            submitter_user = json_object.get('pusher', {}).get('name', {})
            branch = json_object.get('ref', '').split('/').pop()

            message = f"User {submitter_user} ({submitter_email}) pushed to branch {branch}"

        logger.info(message)
    
    except Exception as err:
        error_message = F"{type(err).__name__}: {err} (ID:{request_id})"
        logger.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)
    finally:
        logger.debug(F"Finished ID:{request_id}")

    return "okay"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

if __name__ == "__1main__":
    from mabel.utils.entropy import random_string
    branch_name = 'rosey-' + random_string()
    print(branch_name)

if __name__ == "__1main__":

    import os
    from mabel.utils.entropy import random_string
    from internals.adapters.http import HttpAdapter, GetRequestModel
    from internals.adapters.github import GitHubAdapter, GitHubListReposModel


    import subprocess
    import shutil
    shutil.rmtree('temp', ignore_errors=True)
    os.makedirs('temp', exist_ok=True)
    subprocess.call('git clone https://github.com/joocer/wasure-template.git', shell=True, cwd='temp')


    repos = GitHubListReposModel (
        auth_token=os.environ.get('GITHUB_TOKEN'),
        name='joocer'
    )

    repo_list = GitHubAdapter.list_repos(repos).json()
    for repo in repo_list:
        url = F"https://raw.githubusercontent.com/{repo.get('full_name')}/main/TEMPLATE"
        code, headers, content = HttpAdapter.get(GetRequestModel(url=url))
        content = content.decode().strip()
        if code == 200 and content.startswith("https://github.com/joocer/wasure-template"):

            branch_name = 'rosey-' + random_string()
            print(branch_name)

            shutil.rmtree(F'temp/{repo.get("name")}', ignore_errors=True)
            subprocess.call(F"git clone {repo.get('git_url')}", shell=True, cwd='temp')

            # open a '.templateignore'
            print(F'now compare whats in `wasure-template` with whats in `{repo.get("name")}`')

            shutil.rmtree(F'temp/{repo.get("name")}', ignore_errors=True)