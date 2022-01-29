# pylint: disable=redefined-outer-name, wrong-import-position, unused-argument
import base64
import json
import os
import zlib
from uuid import uuid4
from datetime import datetime, timedelta, timezone

import pytest

os.environ["ENV"] = "local"
os.environ["SERVICE_NAME"] = "kolvir"
os.environ["HOST_NETWORK"] = "host.docker.internal"
os.environ["LOG_LEVEL"] = "INFO"

os.environ["AWS_ACCESS_KEY_ID"] = "TEST"
os.environ["AWS_SECRET_ACCESS_KEY"] = "TEST"
os.environ["AWS_SECURITY_TOKEN"] = "TEST"
os.environ["AWS_SESSION_TOKEN"] = "TEST"
os.environ["AWS_REGION"] = "TEST"

os.environ["JWT_SECRET"] = "TEST"
os.environ["BOTO_ENDPOINT_URL"] = "http://localstack:4566/"
os.environ["PYPI_S3_BUCKET"] = "localstack-s3-pypi-bucket"

from kolvir.api.context import request
from kolvir.token.generate import new_token
from kolvir.util.dot_dict import DotDict
from kolvir.util.logger import set_up_logger

set_up_logger()


@pytest.fixture(scope="module")
def request_context():
    request.context = DotDict(
        {
            "request_id": str(uuid4()),
            "session_id": None,
        }
    )


@pytest.fixture()
def request_context_with_auth(request_context):
    token = new_token(["pypi"], datetime.now(tz=timezone.utc) + timedelta(minutes=1))
    encoded_token = base64.b64encode(token.encode()).decode()
    request.headers = {"Authorization": f"Basic {encoded_token}"}

    def _with_scopes(*scopes):
        token = new_token(scopes, datetime.now(tz=timezone.utc) + timedelta(minutes=1))
        encoded_token = base64.b64encode(token.encode()).decode()
        request.headers = {"Authorization": f"Basic {encoded_token}"}

    yield _with_scopes
    request.headers.pop("Authorization", None)


@pytest.fixture(scope="module")
def request_data(request_context):
    def _request_data(data):
        request.data = DotDict(data)

    yield _request_data
    request.data = None


@pytest.fixture(scope="module")
def get_response_body():
    def _get_response_body(response):
        if response.isBase64Encoded:
            response_body = json.loads(
                zlib.decompress(base64.b64decode(response.body), wbits=31)
            )
        else:
            response_body = json.loads(response.body)
        return response_body

    yield _get_response_body
