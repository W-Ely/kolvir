# pylint: disable=redefined-outer-name, unused-argument
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from kolvir.aws import secretsmanager


class StubException(Exception):
    pass


def test_get_secret_value():
    secret_id = "get_secret_value"
    secret_data = {"secret": "data"}
    with pytest.raises(secretsmanager.AwsNotFoundException):
        secret = secretsmanager.get_secret_value(secret_id)
    secretsmanager.put_secret_value(secret_id, secret_data)
    secret = secretsmanager.get_secret_value(secret_id)
    assert secret["secret"] == "data"
    with patch("kolvir.aws.secretsmanager.get_client") as client:
        client.return_value.exceptions.ResourceNotFoundException = StubException
        client.return_value.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": 429}}, "test"
        )
        with pytest.raises(secretsmanager.AwsException):
            secretsmanager.get_secret_value(secret_id)
    secretsmanager.put_secret_value(secret_id, "data")
    assert secretsmanager.get_secret_value(secret_id) == "data"


def test_put_secret_value():
    secret_id = "put_secret_value"
    secret_data = {"secret": "data"}
    with pytest.raises(secretsmanager.AwsNotFoundException):
        secret = secretsmanager.get_secret_value(secret_id)
    secretsmanager.put_secret_value(secret_id, secret_data)
    secret = secretsmanager.get_secret_value(secret_id)
    assert secret["secret"] == "data"
    with patch("kolvir.aws.secretsmanager.get_client") as client:
        client.return_value.exceptions.ResourceNotFoundException = StubException
        client.return_value.put_secret_value.side_effect = ClientError(
            {"Error": {"Code": 429}}, "test"
        )
        with pytest.raises(secretsmanager.AwsException):
            secretsmanager.put_secret_value(secret_id, secret_data)
    secretsmanager.put_secret_value(secret_id, "data")
    assert secretsmanager.get_secret_value(secret_id) == "data"


def test_create_secret():
    secret_id = "create_secret"
    secret_data = {"secret": "data"}
    with pytest.raises(secretsmanager.AwsNotFoundException):
        secretsmanager.get_secret_value(secret_id)
    secretsmanager.create_secret(secret_id, secret_data)
    with pytest.raises(secretsmanager.AwsResourceExistsException):
        secretsmanager.create_secret(secret_id, secret_data)
    with patch("kolvir.aws.secretsmanager.get_client") as client:
        client.return_value.exceptions.ResourceExistsException = StubException
        client.return_value.create_secret.side_effect = ClientError(
            {"Error": {"Code": 429}}, "test"
        )
        with pytest.raises(secretsmanager.AwsException):
            secretsmanager.create_secret(secret_id, secret_data)
