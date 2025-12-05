"""
Rate Limiting/Throttling for API
"""

from django.core.cache import cache
from django.utils import timezone
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle, UserRateThrottle, SimpleRateThrottle
from api.models import APIKey


class AnonBurstThrottle(AnonRateThrottle):
    """
    Throttle for anonymous users - burst requests
    """

    scope = "anon_burst"
    rate = "20/minute"


class AnonSustainedThrottle(AnonRateThrottle):
    """
    Throttle for anonymous users - sustained requests
    """

    scope = "anon_sustained"
    rate = "100/hour"


class UserBurstThrottle(UserRateThrottle):
    """
    Throttle for authenticated users - burst requests
    """

    scope = "user_burst"
    rate = "60/minute"


class UserSustainedThrottle(UserRateThrottle):
    """
    Throttle for authenticated users - sustained requests
    """

    scope = "user_sustained"
    rate = "1000/hour"


class AuthThrottle(ScopedRateThrottle):
    """
    Throttle for authentication endpoints
    """

    scope = "auth"
    rate = "5/minute"


class PaymentThrottle(ScopedRateThrottle):
    """
    Throttle for payment endpoints
    """

    scope = "payment"
    rate = "10/minute"


class APIKeyHourlyThrottle(SimpleRateThrottle):
    scope = "api_key_hour"

    def get_cache_key(self, request, view):
        api_key = request.META.get("HTTP_X_API_KEY")
        if not api_key:
            return None
        try:
            obj = APIKey.objects.filter(key=api_key, is_active=True).first()
        except Exception:
            obj = None
        if not obj or obj.is_expired():
            return None
        self.limit = int(getattr(obj, "rate_limit_per_hour", 1000) or 1000)
        self.duration = 60 * 60
        self.rate = f"{self.limit}/hour"
        request._api_key_obj = obj
        request._api_key_hour_limit = self.limit
        return f"throttle_apikey_hour_{api_key}"

    def allow_request(self, request, view):
        key = self.get_cache_key(request, view)
        if key is None:
            return True
        now = timezone.now().timestamp()
        history = cache.get(key, [])
        # prune
        history = [ts for ts in history if ts > now - self.duration]
        allowed = len(history) < self.limit
        if allowed:
            history.append(now)
            cache.set(key, history, self.duration)
        else:
            self.wait_seconds = int((history[0] + self.duration) - now) if history else self.duration
        self.history = history
        remaining = max(self.limit - len(history), 0)
        reset = int((history[0] + self.duration) - now) if history else self.duration
        request._rate_limit_info_hour = {
            "limit": self.limit,
            "remaining": remaining,
            "reset": reset,
        }
        return allowed

    def wait(self):
        return getattr(self, 'wait_seconds', 0)


class APIKeyDailyThrottle(SimpleRateThrottle):
    scope = "api_key_day"

    def get_cache_key(self, request, view):
        api_key = request.META.get("HTTP_X_API_KEY")
        if not api_key:
            return None
        obj = getattr(request, "_api_key_obj", None)
        if not obj:
            try:
                obj = APIKey.objects.filter(key=api_key, is_active=True).first()
            except Exception:
                obj = None
        if not obj or obj.is_expired():
            return None
        self.limit = int(getattr(obj, "rate_limit_per_day", 10000) or 10000)
        self.duration = 60 * 60 * 24
        self.rate = f"{self.limit}/day"
        request._api_key_day_limit = self.limit
        return f"throttle_apikey_day_{api_key}"

    def allow_request(self, request, view):
        key = self.get_cache_key(request, view)
        if key is None:
            return True
        now = timezone.now().timestamp()
        history = cache.get(key, [])
        history = [ts for ts in history if ts > now - self.duration]
        allowed = len(history) < self.limit
        if allowed:
            history.append(now)
            cache.set(key, history, self.duration)
        else:
            self.wait_seconds = int((history[0] + self.duration) - now) if history else self.duration
        self.history = history
        remaining = max(self.limit - len(history), 0)
        reset = int((history[0] + self.duration) - now) if history else self.duration
        request._rate_limit_info_day = {
            "limit": self.limit,
            "remaining": remaining,
            "reset": reset,
        }
        return allowed

    def wait(self):
        return getattr(self, 'wait_seconds', 0)
