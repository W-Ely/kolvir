import pytest

from kolvir.api import handler


@pytest.mark.parametrize(
    ("path", "status"),
    [
        pytest.param("/oops", 404, id="/not_found"),
        pytest.param("/health", 200, id="/health"),
        pytest.param("/", 200, id="/root"),
        pytest.param("", 200, id="''"),
        pytest.param("/echo", 200, id="/echo"),
        pytest.param("/500", 500, id="/500"),
    ],
)
def test_api(path, status):
    response = handler.api(
        {
            "path": path,
            "requestContext": {},
            "body": None,
            "httpMethod": "GET",
        },
        "_",
    )
    assert response.statusCode == status


def test_api_broad_exception():
    response = handler.api({"test": "malformed payload"}, "_")
    assert response.statusCode == 500
