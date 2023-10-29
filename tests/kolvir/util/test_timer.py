# pylint: disable=no-member
import logging

from kolvir.util import tools


def test_timer_decorator(caplog):
    logger = logging.getLogger()

    @tools.Timer("test_decorator", logger=logger, level=logging.ERROR)
    def a_test():
        return

    a_test()
    assert len(caplog.records) == 2
    assert "test_decorator - start" in caplog.records[0].message
    assert "test_decorator - elapsed:" in caplog.records[1].message


def test_timer_context_manager(caplog):
    logger = logging.getLogger()
    with tools.Timer("test_decorator", logger=logger, level=logging.ERROR) as timer:
        elapsed_seconds = timer.elapsed()
        assert isinstance(elapsed_seconds, float)
    assert len(caplog.records) == 3
    assert "test_decorator - start" in caplog.records[0].message
    assert "test_decorator - elapsed:" in caplog.records[1].message
    assert "test_decorator - elapsed:" in caplog.records[2].message


def test_timer_explicit_start_stop(caplog):
    logger = logging.getLogger()
    timer = tools.Timer("test_decorator", logger=logger, level=logging.ERROR)
    timer.start()
    elapsed_seconds = timer.stop()
    assert isinstance(elapsed_seconds, float)
    assert len(caplog.records) == 2
    assert "test_decorator - start" in caplog.records[0].message
    assert "test_decorator - elapsed:" in caplog.records[1].message


def test_timer_running_total(caplog):
    logger = logging.getLogger()
    timer = tools.Timer("test_decorator", logger=logger, level=logging.ERROR)
    timer.start()
    for _ in range(5):
        elapsed_seconds = timer.elapsed()
        assert isinstance(elapsed_seconds, float)
    assert len(caplog.records) == 6
    assert "test_decorator - start" in caplog.records[0].message
    for record in caplog.records[1:]:
        assert "test_decorator - elapsed:" in record.message
