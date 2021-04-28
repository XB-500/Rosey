import os
import uvicorn
from fastapi import FastAPI, HTTPException  # type:ignore
from fastapi.responses import UJSONResponse  # type:ignore
from fastapi import Request
from mabel.logging import get_logger, set_log_name
from mabel.data.formats import json

set_log_name("ROSEY")
logger = get_logger()
get_logger().setLevel(15)
app = FastAPI()

@app.get("/health")
def receive_health_check(req: Request):
    try:
        return {"status": "okay"}, 200
    except:
        raise HTTPException(status_code=500, detail="Not Okay")


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

        if github_event == "star":  # check if the event is a star
            nos_stars = json_object["repository"]["stargazers_count"]
            starrer_username = json_object["sender"]["login"]
            repo_url = json_object["repository"]["html_url"]
            repo_name = json_object["repository"]["name"]
            message = f"{starrer_username} has starred the [{repo_name}]({repo_url}). \n\n The Total Stars are {nos_stars}"

        elif github_event == "pull_request":  # check if event is a pull request
            pr_number = json_object["number"]
            if json_object["pull_request"]["merged"] == True:
                pr_action = "merged"
            pr_action = json_object["action"]
            pr_title = json_object["pull_request"]["title"]
            pr_desc = json_object["pull_request"]["body"]
            pr_login = json_object["sender"]["login"]
            pr_login_url = json_object["sender"]["html_url"]
            pr_url = json_object["pull_request"]["html_url"]
            message = f"Pull Request([{pr_number}]({pr_url})) {pr_action} by [{pr_login}]({pr_login_url}).\n\n Title: *{pr_title}* \n\n Description: **{pr_desc}**"

        logger.info(message)
    
    except Exception as err:
        error_message = F"{type(err).__name__}: {err} (ID:{request_id})"
        logger.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)
    finally:
        logger.debug(F"Finished ID:{request_id}")

    return "okay"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=os.environ.get('PORT', 8080))
