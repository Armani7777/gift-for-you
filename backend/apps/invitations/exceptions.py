from __future__ import annotations

from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class InvitationError(APIException):
    status_code = 400
    default_detail = "Something went wrong."
    default_code = "invitation_error"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        super().__init__(detail=detail or self.default_detail)
        if status_code is not None:
            self.status_code = status_code


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data.get("detail", response.data)
    if isinstance(detail, list):
        message = " ".join(str(item) for item in detail)
    elif isinstance(detail, dict):
        message = next(iter(detail.values())) if detail else "Something went wrong."
        if isinstance(message, list):
            message = message[0]
    else:
        message = str(detail)

    response.data = {"error": str(message)}
    return response
