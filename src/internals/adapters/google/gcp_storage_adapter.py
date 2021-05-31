"""
For the times you need direct access to the storage buckets.
"""
import os
from ...errors import MissingDependencyError
try:  # pragma: no cover
    from google.cloud import storage  # type:ignore
    from google.auth.credentials import AnonymousCredentials  # type:ignore
except ImportError:  # pragma: no cover
    storage = None


class CloudStorageAdapter():

    @staticmethod
    def get_blob(project: str, bucket: str, blob_name: str):

        if not storage:  # pragma: no cover
            raise MissingDependencyError("'google-cloud-storage' is missing, install or include in requirements.txt")

        # this means we're testing
        if os.environ.get("STORAGE_EMULATOR_HOST") is not None:  # pragma: no cover
            client = storage.Client(
                credentials=AnonymousCredentials(),
                project=project,
            )
        else:  # pragma: no cover
            client = storage.Client(project=project)

        gcs_bucket = client.get_bucket(bucket)
        blob = gcs_bucket.get_blob(blob_name)
        if blob:
            b = blob.download_as_bytes()
            return b
        return None

    @staticmethod
    def list_blobs(project: str, bucket: str, **kwargs):
        
        if not storage:  # pragma: no cover
            raise MissingDependencyError("'google-cloud-storage' is missing, install or include in requirements.txt")

        # this means we're testing
        if os.environ.get("STORAGE_EMULATOR_HOST") is not None:  # pragma: no cover
            client = storage.Client(
                credentials=AnonymousCredentials(),
                project=project,
            )
        else:  # pragma: no cover
            client = storage.Client(project=project)

        gcs_bucket = client.get_bucket(bucket)
        blobs = list(client.list_blobs(bucket_or_name=gcs_bucket, **kwargs))

        yield from [
            blob.name for blob in blobs if not blob.name.endswith("/")
        ]
        
    @staticmethod
    def save_blob(project: str, bucket: str, path: str, file: str):

        if not storage:  # pragma: no cover
            raise MissingDependencyError("'google-cloud-storage' is missing, install or include in requirements.txt")

        # this means we're testing
        if os.environ.get("STORAGE_EMULATOR_HOST") is not None:  # pragma: no cover
            client = storage.Client(
                credentials=AnonymousCredentials(),
                project=project,
            )
        else:  # pragma: no cover
            client = storage.Client(project=project)
            
        gcs_bucket = client.get_bucket(bucket)
        blob = gcs_bucket.blob(path)
        
        with open(file, 'rb') as content:
            blob.upload_from_string(content.read(), content_type="application/octet-stream")
            
        return True
    
    @staticmethod
    def sync_folder(project: str, bucket: str, target: str, source: str):
        import glob
        
        source_paths = glob.iglob(source + '/**', recursive=True)
        for source_path in source_paths:
            if os.path.isfile(source_path):
                target_path = target + '/' + source_path[len(source)+1:]
                target_path = target_path.replace('\\', '/')
                CloudStorageAdapter().save_blob(
                    project=project,
                    bucket=bucket,
                    path=target_path,
                    file=source_path
                )
        
