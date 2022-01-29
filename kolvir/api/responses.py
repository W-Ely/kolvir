import base64
import json
import zlib
from copy import deepcopy
from http import HTTPStatus

from lambdarest import Response

from kolvir.api.context import context_to_header
from kolvir.util.dot_dict import DotDict

DATA_LIMIT = 20000  # ~20kb,  Lambda response bytes limit is ~6000000 (6mb)

API_GATEWAY_BASE = {
    "isBase64Encoded": False,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Credentials": "True",
    },
}


class ApiResponse(Response):
    def __init__(self, body=None, headers=None, status=HTTPStatus.OK):
        response_base = DotDict(deepcopy(API_GATEWAY_BASE))
        response_base.headers.update(context_to_header())
        if headers is not None:
            response_base.headers.update(headers)
        if body is not None and not isinstance(body, str):
            body = json.dumps(body)
            if should_compress(body):
                body = gzip_b64encode(body)
                update_compression_headers(response_base)
        super().__init__(body=body, status_code=status, **response_base)

    def to_json(
        self, encoder=json.JSONEncoder, application_load_balancer=False
    ):  # pylint: disable=unused-argument
        return self.api_gateway_response()

    def api_gateway_response(self):
        response = DotDict(
            {
                "statusCode": self.status_code,
                "headers": self.headers,
                "isBase64Encoded": self.isBase64Encoded,
            }
        )
        if self.body:
            response.update({"body": self.body})
        return response


class ApiErrorResponse(ApiResponse):
    def __init__(self, *, error, headers=None, status=HTTPStatus.INTERNAL_SERVER_ERROR):
        body = {"message": error, "code": status}
        super().__init__(body=body, headers=headers, status=status)


def should_compress(body):
    if len(body.encode("utf-8")) > DATA_LIMIT:
        return True
    return False


def gzip_b64encode(body):
    comp = zlib.compressobj(wbits=31)
    buffer = comp.compress(body.encode("utf-8")) + comp.flush()
    return base64.b64encode(buffer).decode()


def update_compression_headers(response_base):
    response_base["isBase64Encoded"] = True
    response_base["headers"]["Content-Encoding"] = "gzip"
