import json
from threading import get_ident

from botocore.exceptions import ClientError

from kolvir.aws.shared import (
    AwsException,
    AwsNotFoundException,
    AwsResourceExistsException,
    get_client,
)


# Consider ttl cache here
def get_secret_value(secret_id):
    try:
        client = get_client("secretsmanager", cache_key=get_ident())
        # breakpoint()
        res = client.get_secret_value(SecretId=secret_id)
    except client.exceptions.ResourceNotFoundException as ex:
        raise AwsNotFoundException(f"{ex}, secret_id: {secret_id}") from ex
    except ClientError as ex:
        raise AwsException(f"{ex}, secret_id: {secret_id}") from ex
    try:
        return json.loads(res.get("SecretString"))
    except ValueError:
        return res.get("SecretString")


def put_secret_value(secret_id, secret_data):
    try:
        client = get_client("secretsmanager", cache_key=get_ident())
        return client.put_secret_value(
            SecretId=secret_id,
            SecretString=secret_data
            if isinstance(secret_data, str)
            else json.dumps(secret_data),
        )
    except client.exceptions.ResourceNotFoundException:
        return create_secret(secret_id, secret_data)
    except ClientError as ex:
        raise AwsException(f"{ex}, secret_id: {secret_id}") from ex


def create_secret(secret_id, secret_data):
    try:
        client = get_client("secretsmanager", cache_key=get_ident())
        return client.create_secret(
            Name=secret_id,
            SecretString=secret_data
            if isinstance(secret_data, str)
            else json.dumps(secret_data),
        )
    except client.exceptions.ResourceExistsException as ex:
        raise AwsResourceExistsException(f"{ex}, secret_id: {secret_id}") from ex
    except ClientError as ex:
        raise AwsException(f"{ex}, secret_id: {secret_id}") from ex
