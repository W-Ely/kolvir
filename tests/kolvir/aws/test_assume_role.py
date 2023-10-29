# pylint: disable=unused-argument
from unittest.mock import patch

from kolvir.aws import assume_role
from kolvir.util.dot_dict import DotDict


class MockCache:
    def __init__(self, *args):
        self._cache = {}

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value, *args):
        self._cache[key] = value


@patch("kolvir.aws.assume_role.TTLFileCache", return_value=MockCache())
@patch("builtins.input", return_value="123456")
@patch("subprocess.run")
@patch("sys.exit")
def test_main(*args):
    assume_role.main(
        DotDict({"role": "test", "mfa": True, "duration": 900, "command": "test"})
    )
