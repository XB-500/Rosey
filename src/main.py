from internals import core
from internals.models import TaskStartModel
from internals.flows import sync_repos_flow
from internals.adapters.google import SecretsManagerAdapter, SecretsManagerSecretModel
from fastapi.responses import UJSONResponse  # type:ignore


def load_job_specific_contect(context):
    my_context = context.copy()
    github_token_secret = SecretsManagerSecretModel(secret_id=my_context["GITHUB_TOKEN_KEY"])
    my_context['GITHUB_TOKEN'] = SecretsManagerAdapter.retrieve_secret(github_token_secret)

    return my_context


@core.application.post("/SYNC", response_class=UJSONResponse)
def handle_start_request(request: TaskStartModel):
    my_context = core.load_request_parameters_into_context(request, core.context)
    my_context = load_job_specific_contect(my_context)
    flow = sync_repos_flow(my_context)
    response = core.serve_request(flow, my_context)
    return response


# tell the server to start
if __name__ == "__main__":
    core.start_server()