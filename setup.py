import io
import os.path
import re
from setuptools import find_packages, setup

DISTRO_NAME = "kolvir"
INSTALL_REQUIRES = [
    "boto3>=1.20,<2",
    "PyJWT>=2.3,<3",
]
EXCLUDE = ["kolvir.api*"]


def read(*names, **kwargs):
    with io.open(
        os.path.join(
            os.path.dirname(__file__), *names),
            encoding=kwargs.get("encoding", "utf8"),
    ) as file_path:
        return file_path.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


if __name__ == "__main__":
    setup(
        name=DISTRO_NAME,
        version=find_version(DISTRO_NAME.replace("-", "_"), "__init__.py"),
        url="https://github.com/Hall-of-Mirrors/kolvir",
        maintainer="W. Ely Paysinger",
        maintainer_email="paysinger@gmail.com",
        packages=find_packages(exclude=EXCLUDE),
        install_requires=INSTALL_REQUIRES,
        include_package_data=True,
    )
