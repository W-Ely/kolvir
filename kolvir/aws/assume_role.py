import argparse
import os
import subprocess
import sys

from kolvir.aws import sts
from kolvir.aws.cache import TTLFileCache

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".aws/assume-role/cache")


def main(args):
    arn_split = sts.get_caller_identity()["Arn"].split(":")
    account_id, identity = arn_split[4], arn_split[5]
    role_arn = f"arn:aws:iam::{account_id}:role/{args.role}"
    kwargs = {}
    if args.mfa:
        username = identity.split("/")[-1]
        mfa_serial = f"arn:aws:iam::{account_id}:mfa/{username}"
        kwargs["serial_number"] = mfa_serial
    if args.duration:
        kwargs["duration_seconds"] = args.duration
    cache = TTLFileCache(CACHE_DIR)
    cache_key = f'{role_arn}{kwargs.get("serial_number")}'
    res = cache.get(cache_key)
    if res is None:
        if args.mfa:
            sys.stderr.write("Enter MFA code: ")
            token = input()
            kwargs["token_code"] = token
        res = sts.assume_role(role_arn, identity.replace("/", "-"), **kwargs)
        res["Credentials"]["Expiration"] = (
            res["Credentials"]["Expiration"].strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )
        cache.set(cache_key, res, res["Credentials"]["Expiration"])
    aws_env = {
        "AWS_ACCESS_KEY_ID": res["Credentials"]["AccessKeyId"],
        "AWS_SECRET_ACCESS_KEY": res["Credentials"]["SecretAccessKey"],
        "AWS_SESSION_TOKEN": res["Credentials"]["SessionToken"],
    }
    env = os.environ.copy()
    env.update(aws_env)
    if "AWS_PROFILE" in env:
        del env["AWS_PROFILE"]
    process = subprocess.run(args.command, env=env, check=True)
    sys.exit(process.returncode)


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True, help="Role to assume.")
    parser.add_argument(
        "--mfa", default=False, action="store_true", help="Is MFA required"
    )
    parser.add_argument(
        "--duration", type=int, help="Duration of credentials in seconds"
    )
    parser.add_argument(
        "command", nargs=argparse.REMAINDER, help="The command to execute."
    )
    parsed_args = parser.parse_args()
    main(parsed_args)
