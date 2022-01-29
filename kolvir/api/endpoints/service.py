import os

from kolvir.api.auth import requires_auth, requires_scopes
from kolvir.api.context import request
from kolvir.api.exceptions import exception_handler, Http404
from kolvir.api.lambdarest import lambda_handler
from kolvir.api.responses import ApiResponse

SERVICE_ADMIN_SCOPE = "admin"


@lambda_handler.handle("get", path="/auth")
@exception_handler
@requires_auth
def auth(_):
    return ApiResponse()


@lambda_handler.handle("get", path="/health")
@exception_handler
def health(_):
    return ApiResponse()


@lambda_handler.handle("get", path="/echo")
@exception_handler
def echo(_):
    return ApiResponse(body=request.data)


@lambda_handler.handle("get", path="/environment")
@exception_handler
@requires_scopes(SERVICE_ADMIN_SCOPE)
def environment(_):
    return ApiResponse(body=dict(os.environ.items()))


@lambda_handler.handle("get", path="/500")
@exception_handler
def throw500(_):
    raise ValueError("Oops")


@lambda_handler.handle("get", path="/")
@exception_handler
def root(_):
    return ApiResponse()


@lambda_handler.handle("get", path="/<path:path>")
@exception_handler
def not_found(_):
    raise Http404("not found")
