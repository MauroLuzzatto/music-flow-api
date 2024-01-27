"""
Take from https://github.com/tom-draper/api-analytics
"""
import uuid
from datetime import datetime
from time import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.config import settings
from app.core.aws import upload_json_to_s3


class Analytics(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, is_lambda_runtime: bool, is_testing: bool = False):
        super().__init__(app)
        self.is_lambda_runtime = is_lambda_runtime
        self.is_testing = is_testing

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time()
        response = await call_next(request)

        try:
            ip_address = request.client.host
        except AttributeError:
            ip_address = None

        request_data = {
            "hostname": request.url.hostname,
            "ip_address": ip_address,
            "path": request.url.path,
            "user_agent": request.headers["user-agent"],
            "method": request.method,
            "status": response.status_code,
            "response_time": int((time() - start) * 1000),
            "created_at": datetime.now().isoformat(),
            "environment": "prod" if self.is_lambda_runtime else "dev",
        }
        if self.is_lambda_runtime or self.is_testing:
            save_folder = (
                settings.FOLDER_ACTIVITY if not self.is_testing else "activity_test"
            )
            name = str(uuid.uuid4())
            upload_json_to_s3(
                data_dict=request_data,
                save_name=f"{save_folder}/{name}.json",
            )
        return response
