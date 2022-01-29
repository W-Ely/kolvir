import argparse
from datetime import datetime, timedelta, timezone
import os

import jwt

JWT_SECRET = os.environ.get("JWT_SECRET")
ALGORITHM = "HS256"


def new_token(scopes, expiration):
    return jwt.encode(
        {
            "scopes": scopes,
            "exp": expiration,
        },
        JWT_SECRET,
        algorithm=ALGORITHM,
    )


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--scopes", nargs="+", default=["pypi"])
    parsed_args = parser.parse_args()
    print(
        new_token(parsed_args.scopes, datetime.now(tz=timezone.utc) + timedelta(days=7))
    )
