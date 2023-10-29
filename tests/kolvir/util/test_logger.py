import json
import logging

from kolvir.util import logger

LOGGER = logging.getLogger()


def test_formatter_handles_circular_objects(caplog):
    class Test:
        # __slots__ = ("a","test")
        def __init__(self):
            self.a_a = "a"
            self.test = self

    logging.error("Circular Ref", extra={"test": Test()})
    formatter = logger.JSONFormatter("test")
    formated_record = formatter.format(caplog.records[0])
    record = json.loads(formated_record)
    assert record["test"]["log_error"] == (
        "error creating json log: Circular reference detected"
    )


def test_formatter_handles_objects_no_dict_property(caplog):
    class Test:
        __slots__ = ("a_a", "test")

        def __init__(self):
            self.a_a = "a"
            self.test = self

    logging.error("Circular Ref", extra={"test": Test()})
    formatter = logger.JSONFormatter("test")
    formated_record = formatter.format(caplog.records[0])
    assert ".test_formatter_handles_objects_no_dict_property." in formated_record
