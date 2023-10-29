import base64
import logging
import os
from functools import wraps

import jwt

from kolvir.api.context import request
from kolvir.api.exceptions import Http400, Http401, Http403

JWT_SECRET = os.environ.get("JWT_SECRET")
ALGORITHMS = ["HS256"]


def _get_token():
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise Http400("Bad Request")
    try:
        split_authorization = authorization.split(" ")
        logging.debug(f"1: {split_authorization}")
        if len(split_authorization) == 2:
            encoded_token = split_authorization[1]
        else:
            encoded_token = split_authorization[0]
        base64_decoded_auth = base64.b64decode(encoded_token).decode()
        logging.debug(f"2: {base64_decoded_auth}")
        split_decoded_auth = base64_decoded_auth.split(":")
        logging.debug(f"3: {split_decoded_auth}")
        if len(split_decoded_auth) == 2 and split_decoded_auth[1]:
            token = split_decoded_auth[1]
        else:
            token = split_decoded_auth[0]
    except Exception as ex:
        raise Http400("Bad Request") from ex
    logging.debug(f"4: {token}")
    return token


def requires_scopes(*scopes):
    def wrapper(func):
        @wraps(func)
        def handler(*args, **kwargs):
            token = _get_token()
            try:
                token = jwt.decode(token, JWT_SECRET, algorithms=ALGORITHMS)
            except jwt.InvalidTokenError as ex:
                raise Http401("Unauthorized") from ex
            for scope in scopes:
                if scope not in token["scopes"]:
                    raise Http403("Forbidden")
            return func(*args, **kwargs)

        return handler

    return wrapper


def requires_auth(func):
    @wraps(func)
    def handler(*args, **kwargs):
        token = _get_token()
        try:
            jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.InvalidTokenError as ex:
            raise Http401("Unauthorized") from ex
        return func(*args, **kwargs)

    return handler
