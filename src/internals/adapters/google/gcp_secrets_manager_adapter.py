"""

pip install google-cloud-secret-manager
"""
from google.cloud import secretmanager
from pydantic import BaseModel
from typing import Optional, Union



class SecretsManagerSecretModel(BaseModel):
    project: str
    secret_id: str
    version_id: str = 'latest'


class SecretsManagerAdapter():

    @staticmethod
    def access_secret_version(
            secret: SecretsManagerSecretModel) -> str:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{secret.project_id}/secrets/{secret.secret_id}/versions/{secret.version_id}"

        # Access the secret
        response = client.access_secret_version(name=name)

        # Return the decoded payload
        return response.payload.data.decode('utf8')
