import os

from kolvir.api.auth import requires_scopes
from kolvir.api.exceptions import exception_handler, Http404
from kolvir.api.lambdarest import lambda_handler
from kolvir.api.responses import ApiResponse
from kolvir.aws import s3

EXPIRATION_SECONDS = 900  # 15 minutes
PYPI_S3_BUCKET = os.environ.get("PYPI_S3_BUCKET")
PYPI_SCOPE = "pypi"


@lambda_handler.handle("get", path="/pypi/<string:project>/<string:filename>")
@exception_handler
@requires_scopes(PYPI_SCOPE)
def download(_, project, filename):
    url = s3.generate_presigned_url(
        PYPI_S3_BUCKET, f"{project}/{filename}", EXPIRATION_SECONDS
    )
    return ApiResponse(
        headers={"Location": url},
        status=302,
    )


@lambda_handler.handle("get", path="/pypi/<string:project>")
@exception_handler
@requires_scopes(PYPI_SCOPE)
def list_versions(_, project):
    keys = s3.list_objects(PYPI_S3_BUCKET, prefix=project)
    if not keys:
        raise Http404()
    new_line = "\n"
    list_items = [
        f'<li><a href="{key}/">{key}</a></li>'
        for key in map(lambda x: x.replace(f"{project}/", ""), keys)
    ]
    body = f"<body><ul>\n{new_line.join(list_items)}\n</ul></body>"
    head = f"<head><title>{project}</title></head>"
    html = f"<!DOCTYPE HTML><html>{head}\n{body}\n</html>\n"
    return ApiResponse(
        headers={"Content-Type": "text/html"},
        body=html,
    )
