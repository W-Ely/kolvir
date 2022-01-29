import logging
from functools import wraps
from datetime import datetime


class Timer:
    def __init__(self, name, logger=None, level=logging.INFO):
        self._name = name
        self._logger = logger
        self._level = level
        self._start_time = None

    def start(self):
        self._start_time = datetime.now()
        if self._logger:
            self._logger.log(
                self._level,
                f"Timer: {self._name} - start",
                extra={"timer": {"name": self._name}},
            )
        return self

    def stop(self):
        end_time = datetime.now()
        elapsed_seconds = float(f"{(end_time - self._start_time).total_seconds():.2f}")
        if self._logger:
            self._logger.log(
                self._level,
                f"Timer: {self._name} - elapsed: {elapsed_seconds}",
                extra={
                    "timer": {"name": self._name, "elapsed_seconds": elapsed_seconds}
                },
            )
        return elapsed_seconds

    def elapsed(self):
        return self.stop()

    def __enter__(self):
        return self.start()

    def __exit__(self, *_args):
        self.stop()

    def __call__(self, func):
        @wraps(func)
        def _timer(*args, **kwargs):
            with self.__class__(
                self._name,
                logger=self._logger,
                level=self._level,
            ):
                output = func(*args, **kwargs)
            return output

        return _timer
