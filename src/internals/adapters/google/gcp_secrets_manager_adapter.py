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
import os

try:
    from google.cloud import secretmanager  # type:ignore
except ImportError:  # pragma: no cover
    secretmanager = None  # type:ignore
from typing import Optional
from pydantic import BaseModel  # type:ignore
from ...errors import MissingDependencyError


class SecretsManagerSecretModel(BaseModel):
    project: str = "762690895289"
    secret_id: str
    version_id: str = "latest"


class SecretsManagerAdapter:
    @staticmethod
    def _stubbed_retrieve_secret(secret: SecretsManagerSecretModel) -> Optional[str]:
        """
        Retrieve a Secret from the Environment Variables
        """
        return os.environ.get(secret.secret_id)

    @staticmethod
    def retrieve_secret(
        secret: SecretsManagerSecretModel,
    ) -> Optional[str]:  # pragma: no cover
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

        # if the environment variables are set to stub the secrets manager,
        # retrieve the secret from the environment variables.
        if os.environ.get("STUB_SECRETS_MANAGER", False):
            return SecretsManagerAdapter._stubbed_retrieve_secret(secret)

        if not secretmanager:
            raise MissingDependencyError(
                "`google.cloud.secretmanager` must be installed"
            )

        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{secret.project}/secrets/{secret.secret_id}/versions/{secret.version_id}"

        # Access the secret
        response = client.access_secret_version(name=name)

        # Return the decoded payload
        return response.payload.data.decode("utf8")
