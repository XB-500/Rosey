"""

pip install google-cloud-secret-manager
"""
from google.cloud import secretmanager

class SecretsManagerAdapter():

    @staticmethod
    def access_secret_version(
            project_id: str,
            secret_id: str,
            version_id: str="latest") -> str:

        # Create the Secret Manager client.
        client = secretmanager.SecretManagerServiceClient()

        # Build the resource name of the secret version.
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        # Access the secret version.
        response = client.access_secret_version(name=name)

        # Return the decoded payload.
        return response.payload.data.decode('UTF-8')
