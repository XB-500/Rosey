"""
Google Cloud Platform: Secrets Manager Adapter

Derived from the examples on:
    https://github.com/googleapis/python-secret-manager

requirements:
    google-cloud-secret-manager
    pydantic
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
    def retrieve_secret(
            secret: SecretsManagerSecretModel) -> str:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{secret.project}/secrets/{secret.secret_id}/versions/{secret.version_id}"

        # Access the secret
        response = client.access_secret_version(name=name)

        # Return the decoded payload
        return response.payload.data.decode('utf8')
