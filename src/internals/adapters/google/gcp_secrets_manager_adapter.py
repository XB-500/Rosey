"""
Google Cloud Platform: Secrets Manager Adapter

An interface to Secrets Manager on GCP to assist with performing common
functionality with this component.

Derived from the examples on:
    https://github.com/googleapis/python-secret-manager

requirements:
    google-cloud-secret-manager
    pydantic
"""
try:
    from google.cloud import secretmanager  # type:ignore
except ImportError:
    secretmanager = None
from pydantic import BaseModel  # type:ignore
from ...errors import MissingDependencyError


class SecretsManagerSecretModel(BaseModel):
    project: str
    secret_id: str
    version_id: str = 'latest'


class SecretsManagerAdapter():

    @staticmethod
    def retrieve_secret(
            secret: SecretsManagerSecretModel) -> str:
        """
        Retrieve a Secret from Secrets Manager

        Paramters:
            secret: SecretsManagerSecretModel
                The details of the secret

        Returns:
            String

        Raises:
            MissingDependencyError
                When google.cloud.secretmanager isn't available
        """
        if not secretmanager:
            raise MissingDependencyError("`google.cloud.secretmanager` must be installed")

        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{secret.project}/secrets/{secret.secret_id}/versions/{secret.version_id}"

        # Access the secret
        response = client.access_secret_version(name=name)

        # Return the decoded payload
        return response.payload.data.decode('utf8')
