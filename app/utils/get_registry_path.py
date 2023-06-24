import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def setup() -> Optional[str]:
    """_summary_

    Returns:
        Optional[str]: _description_
    """

    AWS_EXECUTION_ENV = os.environ.get("AWS_EXECUTION_ENV")
    is_lambda_runtime = bool(AWS_EXECUTION_ENV)

    if is_lambda_runtime:
        # lambda can only write to the "/tmp" folder, if we want to download
        # the model from s3 bucket we need to set the path to "/tmp"
        path_registry = "/tmp"
    else:
        path_registry = None

    logger.info(f"AWS_EXECUTION_ENV: {AWS_EXECUTION_ENV}")
    logger.debug(f"is_lambda_runtime: {is_lambda_runtime}")
    logger.debug(f"path_registry: {path_registry}")
    return path_registry
