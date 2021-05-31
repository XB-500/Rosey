"""
HTTP Adapter

Requirements
    urllib
    requests
    pydantic
    mabel
"""
import requests
from urllib.request import urlopen
from pydantic import BaseModel  # type:ignore
from typing import Optional
from mabel.logging import get_logger  # type:ignore


class GetRequestModel(BaseModel):
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    headers: Optional[dict] = {"X-Requested-With": "python-requests"}
    parameters: Optional[dict] = {}


class PostRequestModel(BaseModel):
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    headers: Optional[dict] = {"X-Requested-With": "python-requests"}
    data: Optional[dict] = {}


class HttpAdapter:
    @staticmethod
    def get(request: GetRequestModel) -> tuple:

        if not request.url.startswith("https://") and not request.url.startswith(
            "http://"
        ):
            raise ValueError(
                f"`{request.url}` is not a valid HTTP end-point, HTTP Download Adapter can only be used for HTTP end-points."
            )

        try:
            response = requests.get(
                request.url,
                params=request.parameters if request.parameters else None,
                auth=(request.username, request.password) if request.username else None,
                headers=request.headers if request.headers else None,
            )
            return response.status_code, response.headers, response.content
        except Exception as e:  # pragma: no cover
            get_logger().error(f"GET request failed: {type(e).__name__} - {e}")
        return 500, {}, bytes()  # pragma: no cover

    @staticmethod
    def post(request: PostRequestModel) -> tuple:

        if not request.url.startswith("https://") and not request.url.startswith(
            "http://"
        ):
            raise ValueError(
                f"`{request.url}` is not a valid HTTP end-point, HTTP Download Adapter can only be used for HTTP end-points."
            )

        try:
            response = requests.post(
                request.url,
                data=request.data if request.data else None,
                auth=(request.username, request.password) if request.username else None,
                headers=request.headers if request.headers else None,
            )
            return response.status_code, response.headers, response.content
        except Exception as e:  # pragma: no cover
            get_logger().error(f"POST request failed: {type(e).__name__} - {e}")
        return 500, {}, bytes()  # pragma: no cover
