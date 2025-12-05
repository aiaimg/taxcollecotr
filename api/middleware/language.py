from django.utils.deprecation import MiddlewareMixin
from django.utils import translation


class APIContentLanguageMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            lang = translation.get_language_from_request(request, check_path=False)
            if lang not in {"fr", "mg"}:
                lang = "fr"
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
            request._api_language = lang
        except Exception:
            translation.activate("fr")
            request.LANGUAGE_CODE = "fr"
            request._api_language = "fr"
        return None

    def process_response(self, request, response):
        try:
            lang = getattr(request, "_api_language", None) or translation.get_language() or "fr"
            response["Content-Language"] = lang
        except Exception:
            response["Content-Language"] = "fr"
        return response
