# pylint: disable=redefined-outer-name, unused-argument
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from kolvir.aws import s3

TEST_BUCKET = "test-bucket"


class StubException(Exception):
    pass


@pytest.fixture(scope="module")
def set_s3_data():
    s3.create_bucket(TEST_BUCKET)

    def _data(key, data):
        s3.put_object(TEST_BUCKET, key, data)

    yield _data


def test_head_object(set_s3_data):
    assert not s3.head_object(TEST_BUCKET, "key_not_present")
    set_s3_data("key", {"some": "data"})
    assert s3.head_object(TEST_BUCKET, "key")
    with patch(
        "kolvir.aws.s3.get_client",
        side_effect=ClientError({"Error": {"Code": 429}}, "test"),
    ):
        with pytest.raises(s3.AwsException):
            s3.head_object(TEST_BUCKET, "key")


def test_list_objects(set_s3_data):
    set_s3_data("key", {"some": "data"})
    set_s3_data("key2", {"some": "data"})
    assert len(s3.list_objects(TEST_BUCKET)) == 2
    assert len(s3.list_objects(TEST_BUCKET, prefix="key2")) == 1
    assert len(s3.list_objects(TEST_BUCKET, prefix="key")) == 2
    with patch(
        "kolvir.aws.s3.get_client",
        side_effect=ClientError({"Error": {"Code": 429}}, "test"),
    ):
        with pytest.raises(s3.AwsException):
            s3.list_objects(TEST_BUCKET, prefix="key")


def test_generate_presigned_url(set_s3_data):
    set_s3_data("key", {"some": "data"})
    url = s3.generate_presigned_url(TEST_BUCKET, "key", 10)
    assert TEST_BUCKET in url and "key" in url
    with patch(
        "kolvir.aws.s3.get_client",
        side_effect=ClientError({"Error": {"Code": 429}}, "test"),
    ):
        with pytest.raises(s3.AwsException):
            s3.generate_presigned_url(TEST_BUCKET, "key", 10)


def test_get_json_object(set_s3_data):
    set_s3_data("key", {"some": "data"})
    data = s3.get_json_object(TEST_BUCKET, "key")
    assert data["some"] == "data"
    with patch("kolvir.aws.s3.get_client") as client:
        client.return_value.exceptions.NoSuchKey = StubException
        client.return_value.get_object.side_effect = ClientError(
            {"Error": {"Code": 429}}, "test"
        )
        with pytest.raises(s3.AwsException):
            s3.get_json_object(TEST_BUCKET, "key")


def test_create_bucket():
    s3.create_bucket(TEST_BUCKET)
    s3.create_bucket(TEST_BUCKET, region="us-east-1")
    with patch(
        "kolvir.aws.s3.get_client",
        side_effect=ClientError({"Error": {"Code": 429}}, "test"),
    ):
        with pytest.raises(s3.AwsException):
            s3.create_bucket(TEST_BUCKET)


def test_put_object(set_s3_data):
    s3.put_object(TEST_BUCKET, "key", {"some": "data"})
    data = s3.get_json_object(TEST_BUCKET, "key")
    assert data["some"] == "data"
    with patch(
        "kolvir.aws.s3.get_client",
        side_effect=ClientError({"Error": {"Code": 429}}, "test"),
    ):
        with pytest.raises(s3.AwsException):
            s3.put_object(TEST_BUCKET, "key", {"some": "data"})


def test_delete_object(set_s3_data):
    set_s3_data("key", {"some": "data"})
    s3.delete_object(TEST_BUCKET, "key")
    with pytest.raises(s3.AwsNotFoundException):
        s3.get_json_object(TEST_BUCKET, "key")
    s3.delete_object(TEST_BUCKET, "key_not_present")  # think this should 204
    with patch(
        "kolvir.aws.s3.get_client",
        side_effect=ClientError({"Error": {"Code": 429}}, "test"),
    ):
        with pytest.raises(s3.AwsException):
            s3.delete_object(TEST_BUCKET, "key")
