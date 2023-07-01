import logging
import os


def get_is_lambda_runtime() -> bool:
    AWS_EXECUTION_ENV = os.environ.get("AWS_EXECUTION_ENV")
    is_lambda_runtime = bool(AWS_EXECUTION_ENV)
    logging.info(f"AWS_EXECUTION_ENV: {AWS_EXECUTION_ENV}")
    logging.debug(f"is_lambda_runtime: {is_lambda_runtime}")
    return is_lambda_runtime
