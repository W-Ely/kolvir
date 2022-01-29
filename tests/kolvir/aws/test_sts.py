from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from kolvir.aws import sts


def test_get_caller_identity():
    identity = sts.get_caller_identity()
    assert "UserId" in identity
    assert "Account" in identity
    assert "Arn" in identity
    with patch(
        "kolvir.aws.sts.get_client",
        side_effect=ClientError({"Error": {"Code": 429}}, "test"),
    ):
        with pytest.raises(sts.AwsException):
            sts.get_caller_identity()


def test_assume_role():
    role_arn = "arn:aws:iam::test:role/test"
    role_session_name = "role-test"
    assert sts.assume_role(role_arn, role_session_name)
    kwargs = {
        "duration_seconds": 900,
        "serial_number": "arn:aws:iam::test:mfa/test",
        "token_code": "123456",
    }
    assert sts.assume_role(role_arn, role_session_name, **kwargs)
    with patch(
        "kolvir.aws.sts.get_client",
        side_effect=ClientError({"Error": {"Code": 429}}, "test"),
    ):
        with pytest.raises(sts.AwsException):
            sts.assume_role(role_arn, role_session_name)
