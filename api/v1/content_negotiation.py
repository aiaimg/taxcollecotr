from rest_framework.negotiation import DefaultContentNegotiation


class StrictJSONNegotiation(DefaultContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix=None):
        accept = request.META.get("HTTP_ACCEPT", "")
        if "application/problem+json" in accept and renderers:
            # Allow problem+json by selecting JSON renderer and let views set content-type
            return renderers[0], renderers[0].media_type
        if "/json" in accept or "*/*" in accept or not accept:
            return super().select_renderer(request, renderers, format_suffix)
        # Unsupported Accept -> let DRF raise 406 Not Acceptable
        return super().select_renderer(request, renderers, format_suffix)
