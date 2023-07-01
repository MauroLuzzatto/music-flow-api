import logging
import os
from typing import Optional


def setup(is_lambda_runtime) -> Optional[str]:
    """_summary_

    Returns:
        Optional[str]: _description_
    """
    if is_lambda_runtime:
        # lambda can only write to the "/tmp" folder, if we want to download
        # the model from s3 bucket we need to set the path to "/tmp"
        path_registry = "/tmp"
    else:
        path_registry = None

    logging.debug(f"path_registry: {path_registry}")
    return path_registry
