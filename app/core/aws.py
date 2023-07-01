import json
import logging

import boto3

from app.config import settings

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(settings.LOGGING_LEVEL)


bucket_name = settings.BUCKET_NAME
logger.debug(f"bucket_name: {bucket_name}")

s3_resource = boto3.resource("s3")


def upload_json_to_s3(data_dict: dict, save_name: str) -> bool:
    """this function uploads a file into a defined s3 bucket

    args:
        json_data: json data
        save_name: name of the file in the s3 bucket

    return:
        bool: True if the file was uploaded successfully
    """
    assert save_name.endswith(".json")

    json_data = bytes(json.dumps(data_dict, indent=4).encode("UTF-8"))
    s3object = s3_resource.Object(bucket_name, save_name)
    s3object.put(Body=(json_data))
    logger.debug(f"File uploaded: {save_name}")
    return True


if __name__ == "__main__":
    json_data = {"test": "test"}
    file_name = "test.json"
    upload_json_to_s3(json_data=json_data, file_name=file_name)
