import json
import logging
from threading import get_ident

from botocore.exceptions import ClientError

from kolvir.aws.shared import AwsException, AwsNotFoundException, get_client

LOGGER = logging.getLogger("kolvir.aws.s3")


def head_object(bucket, key):
    try:
        return get_client("s3", cache_key=get_ident()).head_object(
            Bucket=bucket, Key=key
        )
    except ClientError as ex:
        # client.exceptions.NoSuchKey is not thrown in this case ;-/
        if ex.response["Error"]["Code"] == "404":
            return None
        raise AwsException(f"{ex}, bucket: {bucket}, key: {key}") from ex


def list_objects(bucket, prefix=None):
    LOGGER.debug("list_objects", extra={"bucket": bucket, "prefix": prefix})
    kwargs = {"Bucket": bucket}
    if prefix:
        kwargs["Prefix"] = prefix
    try:
        client = get_client("s3", cache_key=get_ident())
        paginator = client.get_paginator("list_objects_v2")
        keys = []
        for page in paginator.paginate(**kwargs):
            try:
                for s3_object in page["Contents"]:
                    keys.append(s3_object["Key"])
            except KeyError:
                break
    except ClientError as ex:
        raise AwsException(f"{ex}, bucket: {bucket}, prefix: {prefix}") from ex
    return keys


def generate_presigned_url(bucket, key, expiration):
    try:
        return get_client("s3", cache_key=get_ident()).generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expiration
        )
    except ClientError as ex:
        raise AwsException(f"{ex}, bucket: {bucket}, key: {key}") from ex


def get_json_object(bucket, key):
    try:
        client = get_client("s3", cache_key=get_ident())
        response = client.get_object(Bucket=bucket, Key=key)
    except client.exceptions.NoSuchKey as ex:
        raise AwsNotFoundException(f"{ex}, bucket: {bucket}, key: {key}") from ex
    except ClientError as ex:
        raise AwsException(f"{ex}, bucket: {bucket}, key: {key}") from ex
    return json.load(response["Body"])


def create_bucket(bucket, region=None):
    try:
        if region is None:
            get_client("s3", cache_key=get_ident()).create_bucket(Bucket=bucket)
        else:
            get_client("s3", region_name=region, cache_key=get_ident()).create_bucket(
                Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": region}
            )
    except ClientError as ex:
        raise AwsException(f"{ex}, bucket: {bucket}, region: {region}") from ex


def put_object(bucket, key, data, encryption=None):
    kwargs = {}
    if encryption:
        kwargs["ServerSideEncryption"] = encryption
    try:
        get_client("s3", cache_key=get_ident()).put_object(
            Body=json.dumps(data), Bucket=bucket, Key=key, **kwargs
        )
    except ClientError as ex:
        raise AwsException(f"{ex}, bucket: {bucket}, key: {key}") from ex


def delete_object(bucket, key):
    try:
        return get_client("s3", cache_key=get_ident()).delete_object(
            Bucket=bucket, Key=key
        )
    except ClientError as ex:
        raise AwsException(f"{ex}, bucket: {bucket}, key: {key}") from ex
