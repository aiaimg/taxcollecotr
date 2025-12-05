"""
RFC 7807 Problem Details exceptions and handler
"""

import logging
import uuid

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from django.utils.translation import get_language, gettext as _

from rest_framework import status
from rest_framework.exceptions import APIException, AuthenticationFailed, NotAuthenticated, Throttled
from rest_framework.response import Response
from rest_framework.views import exception_handler

from api.error_codes import get_error_info

logger = logging.getLogger(__name__)


class RFC7807Exception(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("An error occurred.")
    default_code = "error"

    def __init__(self, detail=None, code=None, status_code=None, type_uri=None, instance=None, errors=None):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.default_code = code
        self.type_uri = type_uri
        self.instance = instance
        self.errors = errors
        super().__init__(detail, code)

    def to_dict(self, correlation_id=None):
        lang = get_language() or "fr"
        info = get_error_info(getattr(self, "default_code", "error"), lang)
        code = getattr(self, "default_code", "error")
        translated = _(f"error.title.{code}")
        title = translated if translated and translated != f"error.title.{code}" else (info.get("title") or self.default_code)
        type_uri = self.type_uri or info.get("type")
        body = {
            "type": type_uri or f"/errors/{self.default_code}",
            "title": title,
            "status": int(getattr(self, "status_code", status.HTTP_400_BAD_REQUEST) or status.HTTP_400_BAD_REQUEST),
            "detail": str(getattr(self, "detail", self.default_detail)),
            "instance": self.instance,
            "code": code,
            "correlationId": correlation_id,
            "language": lang,
        }
        if self.errors is not None:
            body["errors"] = self.errors
        return body


class APIValidationError(RFC7807Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Validation error.")
    default_code = "validation_error"


class AuthenticationError(RFC7807Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Authentication error.")
    default_code = "authentication_error"


class PermissionError(RFC7807Exception):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("Permission denied.")
    default_code = "permission_denied"


class NotFoundError(RFC7807Exception):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("Resource not found.")
    default_code = "not_found"


class RateLimitError(RFC7807Exception):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _("Rate limit exceeded.")
    default_code = "rate_limit"


def _build_problem_response(exc, request, status_code, code, detail=None, errors=None):
    try:
        instance = request.build_absolute_uri() if request else None
    except Exception:
        instance = None
    correlation_id = getattr(request, "correlation_id", None)
    problem = RFC7807Exception(
        detail=detail or getattr(exc, "detail", None),
        code=code,
        status_code=status_code,
        instance=instance,
        errors=errors,
    ).to_dict(correlation_id=correlation_id)
    resp = Response(problem, status=status_code, content_type="application/problem+json")
    try:
        resp["Content-Language"] = get_language() or "fr"
    except Exception:
        resp["Content-Language"] = "fr"
    return resp


def custom_exception_handler(exc, context):
    request = context.get("request") if context else None
    response = exception_handler(exc, context)

    if response is not None:
        code = getattr(exc, "default_code", None)
        if isinstance(exc, Throttled):
            code = "rate_limit"
        if not code:
            sc = int(getattr(response, "status_code", status.HTTP_400_BAD_REQUEST))
            if sc == status.HTTP_404_NOT_FOUND:
                code = "not_found"
            elif sc == status.HTTP_403_FORBIDDEN:
                code = "permission_denied"
            elif sc == status.HTTP_401_UNAUTHORIZED:
                code = "authentication_error"
            elif sc == status.HTTP_429_TOO_MANY_REQUESTS:
                code = "rate_limit"
            elif sc == status.HTTP_400_BAD_REQUEST:
                code = "bad_request"
            else:
                code = "error"
        detail = None
        errors = None
        if hasattr(exc, "detail"):
            if isinstance(exc.detail, (list, dict)):
                errors = exc.detail
            else:
                detail = str(exc.detail)
        return _build_problem_response(exc, request, response.status_code, code, detail=detail, errors=errors)

    if isinstance(exc, Http404):
        return _build_problem_response(exc, request, status.HTTP_404_NOT_FOUND, "not_found", detail=_("Resource not found."))

    if isinstance(exc, PermissionDenied):
        return _build_problem_response(exc, request, status.HTTP_403_FORBIDDEN, "permission_denied", detail=_("Permission denied."))

    if isinstance(exc, DjangoValidationError):
        errors = None
        try:
            errors = exc.message_dict
        except Exception:
            try:
                errors = exc.messages
            except Exception:
                errors = None
        return _build_problem_response(exc, request, status.HTTP_400_BAD_REQUEST, "validation_error", detail=str(exc), errors=errors)

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return _build_problem_response(exc, request, status.HTTP_401_UNAUTHORIZED, "authentication_error")

    if isinstance(exc, Throttled):
        resp = _build_problem_response(
            exc,
            request,
            status.HTTP_429_TOO_MANY_REQUESTS,
            "rate_limit",
            detail=str(getattr(exc, "detail", "Rate limit exceeded.")),
        )
        try:
            wait = int(getattr(exc, "wait", 0))
            if wait > 0:
                resp["Retry-After"] = str(wait)
        except Exception:
            pass
        try:
            info = getattr(request, "_rate_limit_info_hour", None) or getattr(request, "_rate_limit_info_day", None)
            if info:
                resp["X-RateLimit-Limit"] = str(info.get("limit"))
                resp["X-RateLimit-Remaining"] = str(max(info.get("remaining", 0), 0))
                resp["X-RateLimit-Reset"] = str(int(info.get("reset", 0)))
                if "Retry-After" not in resp:
                    resp["Retry-After"] = str(int(info.get("reset", 0)))
        except Exception:
            pass
        return resp

    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return _build_problem_response(exc, request, status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", detail=_("An internal error occurred. Please try again later."))
