# pylint: disable=protected-access
import base64
from contextlib import nullcontext as does_not_raise
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from kolvir.api import auth
from kolvir.api.context import request
from kolvir.api.exceptions import Http400, Http401, Http403
from kolvir.token.generate import new_token


TEST_SCOPE_A = "test:a"
TEST_SCOPE_B = "test:b"


def gen_token(*scopes):
    return new_token(scopes, datetime.now(tz=timezone.utc) + timedelta(minutes=1))


def encode(token):
    encoded_token = base64.b64encode(token.encode()).decode()
    return encoded_token


@pytest.mark.parametrize(
    ("authorization", "context"),
    [
        pytest.param(
            None,
            pytest.raises(Http400),
            id="No Authorization header, raises Http400",
        ),
        pytest.param(
            encode(gen_token()),
            does_not_raise(),
            id="Authorization, no type basic/bearer",
        ),
        pytest.param(
            f"Basic {encode(gen_token())}",
            does_not_raise(),
            id="Basic Authorization, no `:`",
        ),
        pytest.param(
            f"Bearer {encode(gen_token())}",
            does_not_raise(),
            id="Bearer Authorization (in name only ;-)",
        ),
        pytest.param(
            f"Basic {encode(f':{gen_token()}')}",
            does_not_raise(),
            id="Basic Authorization `:` in front ex. `:<token>`",
        ),
        pytest.param(
            f"Basic {encode(f'{gen_token()}:')}",
            does_not_raise(),
            id="Basic Authorization `:` in back ex. `<token>:`",
        ),
        pytest.param(
            "Jibberish",
            pytest.raises(Http400),
            id="Jibberish raises Http400",
        ),
    ],
)
def test__get_token(authorization, context):
    request.headers = {}
    if authorization:
        request.headers = {"Authorization": authorization}
    with context:
        assert "scopes" in jwt.decode(
            auth._get_token(), auth.JWT_SECRET, algorithms=auth.ALGORITHMS
        )


@pytest.mark.parametrize(
    ("authorization", "context"),
    [
        pytest.param(
            None,
            pytest.raises(Http400),
            id="No Authorization header, raises Http400",
        ),
        pytest.param(
            encode(gen_token()),
            pytest.raises(Http403),
            id="No scopes raises Http403",
        ),
        pytest.param(
            encode(gen_token(TEST_SCOPE_A)),
            pytest.raises(Http403),
            id="Not enough scopes raises Http403",
        ),
        pytest.param(
            encode(gen_token()[:-1]),
            pytest.raises(Http401),
            id="Invalid token raises Http401",
        ),
        pytest.param(
            encode(gen_token(TEST_SCOPE_A, TEST_SCOPE_B)),
            does_not_raise(),
            id="Valid token and scopes passes",
        ),
    ],
)
def test_requires_scopes(authorization, context):
    request.headers = {}
    if authorization:
        request.headers = {"Authorization": authorization}

    @auth.requires_scopes(TEST_SCOPE_A, TEST_SCOPE_B)
    def endpoint():
        pass

    with context:
        endpoint()


@pytest.mark.parametrize(
    ("authorization", "context"),
    [
        pytest.param(
            None,
            pytest.raises(Http400),
            id="No Authorization header, raises Http400",
        ),
        pytest.param(
            encode(gen_token(TEST_SCOPE_B)),
            does_not_raise(),
            id="Scopes don't matter, valid token passes.",
        ),
        pytest.param(
            encode(gen_token()[:-1]),
            pytest.raises(Http401),
            id="Invalid token raises Http401",
        ),
        pytest.param(
            encode(gen_token()),
            does_not_raise(),
            id="Valid token passes",
        ),
    ],
)
def test_requires_auth(authorization, context):
    request.headers = {}
    if authorization:
        request.headers = {"Authorization": authorization}

    @auth.requires_auth
    def endpoint():
        pass

    with context:
        endpoint()
