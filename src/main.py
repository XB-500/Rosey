import os
import uvicorn
from internals.flows.store_message_flow import build_flow_store_messages
from fastapi import FastAPI, HTTPException  # type:ignore
from fastapi.responses import UJSONResponse  # type:ignore
from fastapi import Request
from mabel.logging import get_logger, set_log_name
from mabel.data.formats import json
from mabel.utils.common import build_context


set_log_name("ROSEY")
logger = get_logger()

app = FastAPI()

context = build_context()


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
