import logging
import os
from functools import wraps
from http import HTTPStatus

from kolvir.api.responses import ApiErrorResponse

EXC_INFO = os.getenv("LOG_LEVEL") == "DEBUG"
DEFAULT_ERROR_MESSAGE = "Internal Service Error"
LOGGER = logging.getLogger("kolvir.api.exceptions")


class ApiException(Exception):
    status = HTTPStatus.INTERNAL_SERVER_ERROR
    log_level = logging.ERROR
    exc_info = True
    headers = None

    def __init__(self, *args, extra=None):
        super().__init__(*args)
        self.extra = extra or {}


class Http400(ApiException):
    status = HTTPStatus.BAD_REQUEST
    log_level = logging.INFO
    exc_info = EXC_INFO


class Http401(Http400):
    status = HTTPStatus.UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}


class Http403(Http400):
    status = HTTPStatus.FORBIDDEN


class Http404(Http400):
    status = HTTPStatus.NOT_FOUND


class Http500(ApiException):
    status = HTTPStatus.INTERNAL_SERVER_ERROR


def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiException as ex:
            message = str(ex)
            LOGGER.log(ex.log_level, message, extra=ex.extra, exc_info=ex.exc_info)
            return ApiErrorResponse(error=message, headers=ex.headers, status=ex.status)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception(DEFAULT_ERROR_MESSAGE)
            return ApiErrorResponse(
                error=DEFAULT_ERROR_MESSAGE,
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    return wrapper
