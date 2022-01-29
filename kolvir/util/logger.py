import json
import logging
import os
from datetime import datetime

BUILTINS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


def set_up_logger(log_level=None, service="service", context_func=dict):
    formatter = JSONFormatter(service, context_func)
    handlers = logging.getLogger().handlers
    log_level = log_level or os.getenv("LOG_LEVEL") or logging.INFO
    if handlers:
        # AWS Lambda pre-configures a handler that logs to stderr.
        # If a handler is already configured, `.basicConfig` does not execute.
        # Thus we set the level directly.
        logging.getLogger().setLevel(log_level)
        for handler in handlers:
            handler.setFormatter(formatter)
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logging.basicConfig(handlers=[handler], level=log_level)
    logging.captureWarnings(True)


def convert_new_lines(message):
    return " | ".join(message.splitlines())


def extra_from_record(record):
    return {key: value for key, value in record.__dict__.items() if key not in BUILTINS}


class JSONFormatter(logging.Formatter):
    def __init__(self, service, context_func=dict):
        self.service = service
        self.context_func = context_func
        super().__init__()

    def format(self, record):
        message = record.getMessage()
        extra = extra_from_record(record)
        record_dict = self.record_dict(message, extra, record)
        try:
            return json.dumps(
                record_dict, default=lambda x: getattr(x, "__dict__", str(x))
            )
        except Exception as ex:  # pylint: disable=W0703
            # It's pretty rare, but things like cirular references might
            # cause an exception.
            message = record.getMessage()
            record_dict = self.record_dict(  # removing extra in recovery attempt
                message, {"log_error": f"error creating json log: {ex}"}, record
            )
        try:
            return json.dumps(
                record_dict, default=lambda x: getattr(x, "__dict__", str(x))
            )
        except Exception as ex:  # pylint: disable=W0703
            return json.dumps({"message": f"error creating json log: {ex}"})

    def record_dict(self, message, extra, record):
        base = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": convert_new_lines(message),
        }
        if record.exc_info:
            extra["exc_info"] = self.formatException(record.exc_info)
        return {**base, self.service: {**self.context_func(), **extra}}

    def formatException(self, ei):  # pylint: disable=invalid-name
        # Base class uses `ei` for exc_info
        # https://github.com/python/cpython/blob/master/Lib/logging/__init__.py#L620
        return convert_new_lines(super().formatException(ei))
