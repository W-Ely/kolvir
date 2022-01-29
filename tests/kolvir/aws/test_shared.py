from kolvir.aws import shared


def test_get_client():
    client = shared.get_client("s3")
    assert client


def test_aws_exception():
    try:
        raise shared.AwsException("Oops")
    except shared.AwsException as ex:
        assert str(ex) == "Oops"
