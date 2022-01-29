import json
from threading import local
from uuid import uuid4

from kolvir.util.dot_dict import DotDict

request = local()


def set_request_context(event):
    request.__dict__.clear()
    headers = event.get("headers") or {}
    request.context = DotDict(
        {
            "request_id": headers.get("X-Request-ID", str(uuid4())),
            "session_id": headers.get("X-Session-ID"),
            "path": event["path"],
            "method": event["httpMethod"],
            "requested_by": headers.get("X-Requested-By", "unknown-caller"),
        }
    )
    request.headers = headers
    request.data = DotDict(
        {
            "body": json.loads(event["body"]) if event.get("body") else {},
            "path_parameters": event.get("pathParameters") or {},
            "query_string_parameters": event.get("queryStringParameters") or {},
        }
    )


def get_request_context():
    try:
        return request.context
    except AttributeError:
        return {}


def context_to_header():
    try:
        return DotDict(
            {
                "X-Request-ID": request.context.request_id,
                "X-Session-ID": request.context.session_id,
            }
        )
    except AttributeError:
        return DotDict({})
