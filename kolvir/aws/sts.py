from threading import get_ident

from botocore.exceptions import ClientError

from kolvir.aws.shared import AwsException, get_client


def get_caller_identity():
    try:
        return get_client("sts", cache_key=get_ident()).get_caller_identity()
    except ClientError as ex:
        raise AwsException("Failed to get_caller_identity") from ex


def assume_role(
    role_arn,
    role_session_name,
    serial_number=None,
    token_code=None,
    duration_seconds=None,
):
    kwargs = {
        "RoleArn": role_arn,
        "RoleSessionName": role_session_name,
    }
    if serial_number:
        kwargs["SerialNumber"] = serial_number
        kwargs["TokenCode"] = token_code
    if duration_seconds:
        kwargs["DurationSeconds"] = duration_seconds
    try:
        return get_client("sts", cache_key=get_ident()).assume_role(**kwargs)
    except ClientError as ex:
        raise AwsException(f"Failed to assume_role: {role_session_name}") from ex
