import logging
import time

from kolvir.api.context import get_request_context, set_request_context
from kolvir.api.exceptions import DEFAULT_ERROR_MESSAGE
from kolvir.api.responses import ApiErrorResponse
from kolvir.api.router import lambda_handler
from kolvir.util.logger import set_up_logger

LOGGER = logging.getLogger("kolvir.api.handler")
SERVICE_LOG_KEY = "kolvir"

set_up_logger(service=SERVICE_LOG_KEY, context_func=get_request_context)


def api(event, _):
    try:
        start_time = time.time()
        LOGGER.debug("Event", extra={"event": event})
        shim(event)
        set_request_context(event)
        LOGGER.info("Incoming request")
        response = lambda_handler(event=event)
        extra = {
            "status_code": int(response["statusCode"]),
            "elapsed_seconds": float(f"{time.time() - start_time:.2f}"),
        }
        LOGGER.info("Outgoing response", extra=extra)
        LOGGER.debug("Response", extra={"response": response})
        return response
    except Exception:  # pylint: disable=W0703
        LOGGER.exception(DEFAULT_ERROR_MESSAGE)
        return ApiErrorResponse(error=DEFAULT_ERROR_MESSAGE).api_gateway_response()


def shim(event):
    path = event["path"].rstrip("/")  # All paths with and without `/` route the same
    if len(path) == 0:  # Lambdarest fails on root `/`
        path = "//"  # This is a workaround for ^
    event.update({"resource": path, "path": path})  # Workaround for using {any+}
