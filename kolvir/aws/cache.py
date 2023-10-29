import os
import hashlib
import json
from datetime import datetime, timezone


def is_expired(expiration):
    expiration = datetime.strptime(expiration, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    now = datetime.now(timezone.utc)
    time_to_expiration = expiration - now
    time_to_expiration_seconds = (
        time_to_expiration.days * 24 * 60 * 60 + time_to_expiration.seconds
    )
    extra_seconds_as_buffer = 30
    return time_to_expiration_seconds < extra_seconds_as_buffer


def filename(key):
    return hashlib.sha1(f"{key}".encode("utf-8")).hexdigest() + ".json"


class TTLFileCache:
    def __init__(self, cache_dir):
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir, mode=0o755)
        self.cache_dir = cache_dir

    def get(self, key):
        path = os.path.join(self.cache_dir, filename(key))
        try:
            with open(path, encoding="utf-8") as file:
                entry = json.load(file)
        except (
            FileNotFoundError,
            PermissionError,
            IsADirectoryError,
            json.decoder.JSONDecodeError,
        ):
            return None
        if is_expired(entry["expiration"]):
            os.remove(path)
            return None
        return entry["value"]

    def set(self, key, value, expiration):
        path = os.path.join(self.cache_dir, filename(key))
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT, 0o600), "w") as f:
            f.write(json.dumps({"value": value, "expiration": expiration}))
