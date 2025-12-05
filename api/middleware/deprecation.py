import re
from datetime import datetime
from django.conf import settings


class DeprecationHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._rules = []
        for rule in getattr(settings, "DEPRECATED_ENDPOINTS", []):
            pattern = re.compile(rule.get("pattern", ""))
            sunset = rule.get("sunset")
            doc = rule.get("doc_url")
            self._rules.append((pattern, sunset, doc))

    def __call__(self, request):
        response = self.get_response(request)
        try:
            path = request.path
            for pattern, sunset, doc in self._rules:
                if pattern.search(path):
                    response["Deprecation"] = "true"
                    if sunset:
                        # Expect RFC 1123 date string
                        response["Sunset"] = sunset
                    if doc:
                        response["Link"] = f"<{doc}>; rel=\"deprecation\"; type=\"text/html\""
                    break
        except Exception:
            pass
        return response

