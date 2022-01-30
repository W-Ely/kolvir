import os
from functools import lru_cache

from boto3.session import Session

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
BOTO_ENDPOINT_URL = os.getenv("BOTO_ENDPOINT_URL")


class AwsException(Exception):
    pass


class AwsNotFoundException(AwsException):
    pass


class AwsResourceExistsException(AwsException):
    pass


@lru_cache  # These lru caches store a client per thread for thread safe reuse
def get_session(cache_key=None):  # pylint:  disable=unused-argument
    return Session()


@lru_cache
def get_client(service, region_name=None, endpoint_url=None, cache_key=None):
    kwargs = {"region_name": region_name or AWS_REGION}
    if endpoint_url or BOTO_ENDPOINT_URL:
        kwargs["endpoint_url"] = endpoint_url or BOTO_ENDPOINT_URL
    return get_session(cache_key=cache_key).client(service, **kwargs)
