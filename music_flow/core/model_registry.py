import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional
import logging

from music_flow.core.utils import path_registry, path_results
from music_flow.config.core import settings

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Model Registry class, uploads and downloads models to a s3 bucket"""

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.path_registry = path_results
        self.path_results = path_results

    def upload_folder(
        self, folder_name: str, exclude_folders: Optional[list[str]] = None
    ):
        """upload local folder to s3 bucket folder

        Args:
            folder_name (str): _description_
            exclude_folders (Optional[list[str]], optional): _description_. Defaults to None.
        """
        path_upload = os.path.join(self.path_results, folder_name)

        s3_resource = boto3.resource("s3")
        s3_bucket = s3_resource.Bucket(self.bucket_name)

        if not exclude_folders:
            exclude_folders = ["logs", "plots", "results"]

        folder_name = path_upload.split("/")[-1]
        logger.debug(f"folder_name: {folder_name}")

        for path, _, files in os.walk(path_upload):
            path = path.replace("\\", "/")
            directory_name = path.replace(path_upload, "")

            if directory_name[1:] in exclude_folders:
                logger.debug(f"Skipping: {directory_name}")
                continue

            for file in files:
                local_file_name = os.path.join(path, file)
                s3_object_name = f"{folder_name}{directory_name}/{file}"
                logger.info(f"upload: {s3_object_name}")
                try:
                    s3_bucket.upload_file(local_file_name, s3_object_name)
                except ClientError as e:
                    print(e)

    def download_folder(self, folder_name: str):
        """download s3 folder to local path

        Args:
            folder_name (str): _description_
        """
        s3_client = boto3.client("s3")
        s3_resource = boto3.resource("s3")
        paginator = s3_client.get_paginator("list_objects")

        for result in paginator.paginate(
            Bucket=self.bucket_name, Delimiter="/", Prefix=folder_name
        ):
            if result.get("CommonPrefixes"):
                for subdir in result.get("CommonPrefixes"):
                    self.download_folder(subdir.get("Prefix"))

            for file in result.get("Contents", []):
                path_destination = os.path.join(self.path_registry, file.get("Key"))
                logger.info(f"download: {path_destination}")
                if not os.path.exists(os.path.dirname(path_destination)):
                    os.makedirs(os.path.dirname(path_destination))

                if not file.get("Key").endswith("/"):
                    s3_resource.meta.client.download_file(
                        self.bucket_name, file.get("Key"), path_destination
                    )


if __name__ == "__main__":
    registry = ModelRegistry(bucket_name=settings.BUCKET_NAME)
    for folder_name in os.listdir(path_results):
        registry.upload_folder(folder_name)
        registry.download_folder(folder_name)