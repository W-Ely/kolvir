# pylint: disable=unused-argument
import json

from kolvir.api.endpoints import service
from kolvir.api import responses


def test_auth_no_header():
    response = service.auth({})
    assert response.status_code == 400
    assert isinstance(response, responses.ApiResponse)


def test_auth(request_context_with_auth):
    response = service.auth({})
    assert response.status_code == 200
    assert isinstance(response, responses.ApiResponse)


def test_environment(request_context_with_auth):
    response = service.environment({})
    assert response.status_code == 403
    request_context_with_auth(service.SERVICE_ADMIN_SCOPE)
    response = service.environment({})
    assert response.status_code == 200
    assert isinstance(response, responses.ApiResponse)


def test_root(request_context):
    response = service.root({})
    assert response.status_code == 200
    assert isinstance(response, responses.ApiResponse)


def test_not_found(request_context):
    response = service.not_found({})
    assert response.status_code == 404
    assert isinstance(response, responses.ApiErrorResponse)


def test_health_200(request_context):
    response = service.health({})
    assert response.status_code == 200
    assert isinstance(response, responses.ApiResponse)


def test_echo_200(request_context, request_data):
    data = {
        "body": {},
        "method": "GET",
        "query_string_parameters": {"test": "test,test"},
    }
    request_data(data)
    response = service.echo({})
    assert response.status_code == 200
    assert isinstance(response, responses.ApiResponse)
    assert response.body == json.dumps(data)
