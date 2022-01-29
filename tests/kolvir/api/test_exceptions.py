# pylint: disable=unused-argument
from copy import deepcopy

import pytest

from kolvir.api import exceptions as e
from kolvir.api.context import context_to_header
from kolvir.api.responses import ApiErrorResponse, API_GATEWAY_BASE


@pytest.mark.parametrize(
    "exception, expected",
    [
        pytest.param(
            e.Http400("Test 400"),
            {
                "body": '{"message": "Test 400", "code": 400}',
                "statusCode": 400,
            },
            id="Catch Http400, return 400 ApiErrorResponse",
        ),
        pytest.param(
            e.Http404("Test 404"),
            {
                "body": '{"message": "Test 404", "code": 404}',
                "statusCode": 404,
            },
            id="Catch Http404, return 404 ApiErrorResponse",
        ),
        pytest.param(
            e.Http500("Test 500"),
            {
                "body": '{"message": "Test 500", "code": 500}',
                "statusCode": 500,
            },
            id="Catch Http500, return 500 ApiErrorResponse",
        ),
        pytest.param(
            e.ApiException("Base Error Becomes 500"),
            {
                "body": '{"message": "Base Error Becomes 500", "code": 500}',
                "statusCode": 500,
            },
            id="Catch ApiException, return 500 ApiErrorResponse",
        ),
        pytest.param(
            KeyError("Common Exception becomes 500"),
            {
                "body": f'{{"message": "{e.DEFAULT_ERROR_MESSAGE}", "code": 500}}',
                "statusCode": 500,
            },
            id="Catch common exception, return 500 ApiErrorResponse",
        ),
        pytest.param(
            Exception("Base Exception becomes 500"),
            {
                "body": f'{{"message": "{e.DEFAULT_ERROR_MESSAGE}", "code": 500}}',
                "statusCode": 500,
            },
            id="Catch base Exception, return 500 ApiErrorResponse",
        ),
    ],
)
def test_exception_handler(exception, expected, request_context):
    @e.exception_handler
    def raise_exception(exception):
        raise exception

    expected.update(**deepcopy(API_GATEWAY_BASE))
    expected["headers"].update(**context_to_header())
    response = raise_exception(exception)
    assert response.to_json() == expected
    assert isinstance(response, ApiErrorResponse)
