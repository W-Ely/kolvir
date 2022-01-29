# pylint: disable=unused-argument
import base64
import json
import zlib
from copy import deepcopy
from http import HTTPStatus
from unittest.mock import patch

import pytest

from kolvir.api import responses
from kolvir.api.context import context_to_header


@pytest.mark.parametrize(
    ("body", "status", "expected"),
    [
        pytest.param(
            None,
            HTTPStatus.OK,
            {"statusCode": 200},
            id="No data, OK, 200",
        ),
        pytest.param(
            "success",
            HTTPStatus.CREATED,
            {"body": "success", "statusCode": 201},
            id="success, CREATED, 201",
        ),
        pytest.param(
            {"success": {"a": "test"}},
            HTTPStatus.ACCEPTED,
            {
                "body": '{"success": {"a": "test"}}',
                "statusCode": 202,
            },
            id="dict, ACCEPTED, 202",
        ),
    ],
)
def test_api_response(body, status, expected, request_context):
    expected.update(**deepcopy(responses.API_GATEWAY_BASE))
    expected["headers"].update(**context_to_header())
    response = responses.ApiResponse(body=body, status=status).to_json()
    assert response == expected
    assert response.statusCode


@pytest.mark.parametrize(
    ("error", "status", "expected"),
    [
        pytest.param(
            "Oops",
            HTTPStatus.BAD_REQUEST,
            {
                "body": '{"message": "Oops", "code": 400}',
                "statusCode": 400,
            },
            id="Oops, BAD_REQUEST, 400",
        ),
        pytest.param(
            "Lower Expectations",
            HTTPStatus.EXPECTATION_FAILED,
            {
                "body": '{"message": "Lower Expectations", "code": 417}',
                "statusCode": 417,
            },
            id="Lower Expectations, EXPECTATION_FAILED, 417",
        ),
    ],
)
def test_api_error_response(error, status, expected, request_context):
    expected.update(**deepcopy(responses.API_GATEWAY_BASE))
    expected["headers"].update(**context_to_header())
    response = responses.ApiErrorResponse(error=error, status=status).to_json()
    assert response == expected
    assert response.statusCode


def test_response_compression(request_context):
    with patch.object(responses, "DATA_LIMIT", 0):
        response = responses.ApiResponse(body={"test": "test"}, status=HTTPStatus.OK)
        assert response.isBase64Encoded is True
        assert response.headers["Content-Encoding"] == "gzip"


def test_should_compress():
    with patch.object(responses, "DATA_LIMIT", 0):
        assert responses.should_compress("test") is True


@pytest.mark.parametrize(
    ("data"),
    [
        pytest.param("testing", id="example 1"),
        pytest.param({"test": "test"}, id="example: 2"),
        pytest.param({"你好": {"世界": ["你好世界"]}}, id="example: 3"),
        pytest.param(["a", "b", "c"], id="example: 4"),
    ],
)
def test_gzip_b64encode(data):
    body = json.dumps(data)
    zipped = responses.gzip_b64encode(body)
    assert json.loads(zlib.decompress(base64.b64decode(zipped), wbits=31)) == data
