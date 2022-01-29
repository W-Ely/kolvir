# pylint: disable=unused-argument
import os

from kolvir.api.endpoints import pypi
from kolvir.api import responses
from kolvir.aws import s3

PYPI_S3_BUCKET = os.environ.get("PYPI_S3_BUCKET")


def test_download(request_context_with_auth):
    request_context_with_auth(pypi.PYPI_SCOPE)
    response = pypi.download({}, "test", "test")
    assert response.status_code == 302
    assert "Location" in response.headers
    assert isinstance(response, responses.ApiResponse)


def test_list_versions(request_context_with_auth):
    request_context_with_auth(pypi.PYPI_SCOPE)
    s3.create_bucket(PYPI_S3_BUCKET)
    response = pypi.list_versions({}, "test")
    assert response.status_code == 404
    s3.put_object(PYPI_S3_BUCKET, "test/test.1", {"test": 1})
    s3.put_object(PYPI_S3_BUCKET, "test/test.2", {"test": 2})
    response = pypi.list_versions({}, "test")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html"
    assert '<li><a href="test.1/">test.1</a></li>' in response.body
