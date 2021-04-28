import uvicorn
from fastapi import FastAPI  # type:ignore
from fastapi.responses import UJSONResponse  # type:ignore
from fastapi import Request
from mabel.logging import get_logger, set_log_name
from mabel.data.formats import json

set_log_name("ROSEY")
logger = get_logger()
app = FastAPI()

@app.get("/health")
def receive_health_check(req: Request):
    try:
        return {"status": "okay"}, 200
    except:
        return {"status": "failed"}, 500


@app.post("/hook")
async def receive_web_hook(request: Request):

    request_id = -1
    
    try:

        body = b''
        async for chunk in request.stream():
            body += chunk

        request_id = abs(hash(body))
        body = json.parse(body)
        
        github_event = req.headers.get("X-Github-Event")
        logger.debug(F"Started ID: {request_id} - {github_event}")

        # default message
        message = f"Event Received {github_event} \n\n {body}"

        if github_event == "star":  # check if the event is a star
            nos_stars = body["repository"]["stargazers_count"]
            starrer_username = body["sender"]["login"]
            repo_url = body["repository"]["html_url"]
            repo_name = body["repository"]["name"]
            message = f"{starrer_username} has starred the [{repo_name}]({repo_url}). \n\n The Total Stars are {nos_stars}"

        elif github_event == "pull_request":  # check if event is a pull request
            pr_number = body["number"]
            if body["pull_request"]["merged"] == True:
                pr_action = "merged"
            pr_action = body["action"]
            pr_title = body["pull_request"]["title"]
            pr_desc = body["pull_request"]["body"]
            pr_login = body["sender"]["login"]
            pr_login_url = body["sender"]["html_url"]
            pr_url = body["pull_request"]["html_url"]
            message = f"Pull Request([{pr_number}]({pr_url})) {pr_action} by [{pr_login}]({pr_login_url}).\n\n Title: *{pr_title}* \n\n Description: **{pr_desc}**"

        logger.info(message)
    
    except Exception as err:
        error_message = F"{type(err).__name__}: {err} (ID:{request_id})"
        logger.error(error_message)
        return {}, 500
    finally:
        logger.debug(F"Finished ID:{request_id}")

    return {}, 200


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
