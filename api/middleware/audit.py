import json
import time
import uuid

from django.utils.deprecation import MiddlewareMixin
import logging

from api.models import APIAuditLog, APIKey
from api.metrics import REQUEST_COUNT, ERROR_COUNT, RESPONSE_TIME, RATE_LIMITED_COUNT
from api.utils.masking import mask_payload


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests/responses with correlation ID and masking
    """

    header_name = 'X-Correlation-ID'

    def process_request(self, request):
        cid = request.META.get('HTTP_X_CORRELATION_ID')
        if not cid:
            cid = uuid.uuid4().hex
        request.correlation_id = cid
        request._audit_start_time = time.time()
        return None

    def process_response(self, request, response):
        try:
            correlation_id = getattr(request, 'correlation_id', uuid.uuid4().hex)
            duration_ms = None
            if hasattr(request, '_audit_start_time'):
                duration_ms = int((time.time() - request._audit_start_time) * 1000)

            # Extract API key if present
            api_key_obj = None
            api_key = request.META.get('HTTP_X_API_KEY')
            if api_key:
                try:
                    api_key_obj = APIKey.objects.filter(key=api_key).first()
                except Exception:
                    api_key_obj = None

            # Parse request body as JSON if possible; fallback to query params
            req_body = {}
            try:
                if request.body:
                    req_body = json.loads(request.body.decode('utf-8'))
            except Exception:
                req_body = {}
            if not req_body:
                try:
                    if request.method == 'GET':
                        req_body = {k: v for k, v in request.GET.items()}
                    elif request.POST:
                        req_body = {k: v for k, v in request.POST.items()}
                except Exception:
                    pass

            # Build headers (limited for privacy)
            headers = {}
            for k, v in request.META.items():
                if k.startswith('HTTP_') and k not in {'HTTP_COOKIE'}:
                    headers[k] = v

            # Parse response body as JSON if possible
            resp_body = {}
            try:
                content = getattr(response, 'content', b'')
                if content:
                    resp_body = json.loads(content.decode('utf-8'))
            except Exception:
                resp_body = {}

            # Attach rate limit info into response body for audit tracking
            try:
                hour_info = getattr(request, '_rate_limit_info_hour', None)
                day_info = getattr(request, '_rate_limit_info_day', None)
                info = hour_info or day_info
                if info and isinstance(resp_body, dict):
                    resp_body['rate_limit'] = {
                        'limit': info.get('limit'),
                        'remaining': info.get('remaining'),
                        'reset': info.get('reset'),
                    }
            except Exception:
                pass

            try:
                sc = int(getattr(response, 'status_code', 0))
                if sc >= 400:
                    code = None
                    if isinstance(resp_body, dict):
                        code = resp_body.get('code') or (resp_body.get('error') or {}).get('code')
                    log_payload = {
                        'correlation_id': correlation_id,
                        'endpoint': request.path,
                        'status_code': sc,
                        'code': code,
                    }
                    logging.getLogger('api.errors').info(json.dumps(log_payload))
                    ERROR_COUNT.labels(
                        endpoint=request.path,
                        method=request.method,
                        error_type=str(code or sc),
                        api_key=(api_key_obj.key if api_key_obj else ""),
                    ).inc()
            except Exception:
                pass

            # Rate limit headers on all responses (if computed by throttles)
            try:
                hour_info = getattr(request, '_rate_limit_info_hour', None)
                day_info = getattr(request, '_rate_limit_info_day', None)
                info = hour_info or day_info
                if info:
                    response['X-RateLimit-Limit'] = str(info.get('limit'))
                    response['X-RateLimit-Remaining'] = str(max(info.get('remaining', 0), 0))
                    response['X-RateLimit-Reset'] = str(int(info.get('reset', 0)))
                    if int(getattr(response, 'status_code', 0)) == 429:
                        response['Retry-After'] = response.get('Retry-After') or str(int(info.get('reset', 0)))
                    # Also attach into response_body for audit tracking
            except Exception:
                pass

            APIAuditLog.objects.create(
                correlation_id=correlation_id,
                endpoint=request.path,
                method=request.method,
                status_code=getattr(response, 'status_code', 0),
                duration_ms=duration_ms,
                client_ip=(request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')),
                api_key=api_key_obj,
                user=(getattr(request, 'user', None) if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False) else None),
                request_headers=headers,
                request_body=mask_payload(req_body),
                response_body=mask_payload(resp_body),
            )

            try:
                sc = int(getattr(response, 'status_code', 0))
                REQUEST_COUNT.labels(
                    endpoint=request.path,
                    method=request.method,
                    status_code=str(sc),
                    api_key=(api_key_obj.key if api_key_obj else ""),
                ).inc()
                if duration_ms is not None:
                    RESPONSE_TIME.labels(
                        endpoint=request.path,
                        method=request.method,
                        status_code=str(sc),
                        api_key=(api_key_obj.key if api_key_obj else ""),
                    ).observe(duration_ms / 1000.0)
                if sc == 429:
                    RATE_LIMITED_COUNT.labels(
                        endpoint=request.path,
                        method=request.method,
                        api_key=(api_key_obj.key if api_key_obj else ""),
                    ).inc()
            except Exception:
                pass

            # Attach correlation ID to response header
            try:
                response[self.header_name] = correlation_id
            except Exception:
                pass

            # Add correlationId to success JSON responses
            try:
                status_code = getattr(response, 'status_code', 0)
                if 200 <= int(status_code) < 300:
                    if hasattr(response, 'data') and isinstance(getattr(response, 'data'), dict):
                        if 'correlationId' not in response.data:
                            response.data['correlationId'] = correlation_id
                        try:
                            if hasattr(response, 'render'):
                                response._is_rendered = False
                                response.render()
                        except Exception:
                            pass
            except Exception:
                pass

            # Rate limit headers from request context (hour/day)
            try:
                hour_info = getattr(request, '_rate_limit_info_hour', None)
                day_info = getattr(request, '_rate_limit_info_day', None)
                info = hour_info or day_info
                if info:
                    response['X-RateLimit-Limit'] = str(info.get('limit'))
                    response['X-RateLimit-Remaining'] = str(max(info.get('remaining', 0), 0))
                    response['X-RateLimit-Reset'] = str(int(info.get('reset', 0)))
            except Exception:
                pass

        except Exception:
            # Avoid breaking the response due to logging failures
            pass

        return response
