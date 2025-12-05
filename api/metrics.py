from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "api_request_total",
    "Total API requests",
    ["endpoint", "method", "status_code", "api_key"],
)

ERROR_COUNT = Counter(
    "api_error_total",
    "Total API errors",
    ["endpoint", "method", "error_type", "api_key"],
)

RESPONSE_TIME = Histogram(
    "api_response_time_seconds",
    "API response time",
    ["endpoint", "method", "status_code", "api_key"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)

RATE_LIMITED_COUNT = Counter(
    "api_rate_limited_total",
    "Total rate-limited responses",
    ["endpoint", "method", "api_key"],
)
