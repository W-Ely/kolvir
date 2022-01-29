from uuid import UUID

from kolvir.api import context


def test_get_request_context():
    context.set_request_context({"path": "/", "httpMethod": "get"})
    request_id = context.get_request_context().request_id
    assert request_id == str(UUID(request_id, version=4))
    context.request.__dict__.clear()
    request_context = context.get_request_context()
    assert request_context == {}


def test_context_to_header():
    context.set_request_context({"path": "/", "httpMethod": "get"})
    header = context.context_to_header()
    request_id = context.get_request_context().request_id
    assert header["X-Request-ID"] == str(UUID(request_id, version=4))
    context.request.__dict__.clear()
    assert context.context_to_header() == {}
