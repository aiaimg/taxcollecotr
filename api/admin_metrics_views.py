from datetime import timedelta

from django.contrib import admin
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from api.models import APIAuditLog, APIKey


def metrics_dashboard_view(request):
    return render(request, "admin/metrics_dashboard.html")


def metrics_usage_data(request):
    now = timezone.now()
    start = now - timedelta(days=30)
    qs = (
        APIAuditLog.objects.filter(timestamp__gte=start)
        .values("api_key__key")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    data = {row["api_key__key"] or "": row["count"] for row in qs}
    return JsonResponse({"usage_by_api_key": data})


def metrics_error_data(request):
    now = timezone.now()
    start = now - timedelta(days=30)
    qs = (
        APIAuditLog.objects.filter(timestamp__gte=start, status_code__gte=400)
        .values("status_code")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    data = {str(row["status_code"]): row["count"] for row in qs}
    return JsonResponse({"errors_by_status": data})


def metrics_performance_data(request):
    now = timezone.now()
    start = now - timedelta(days=7)
    qs = (
        APIAuditLog.objects.filter(timestamp__gte=start, duration_ms__isnull=False)
        .values("endpoint")
        .annotate(avg_ms=Avg("duration_ms"), count=Count("id"))
        .order_by("-avg_ms")
    )
    data = [
        {"endpoint": row["endpoint"], "avg_ms": float(row["avg_ms"] or 0), "count": row["count"]}
        for row in qs
    ]
    return JsonResponse({"performance": data})


def metrics_timeseries_data(request):
    now = timezone.now()
    start = now - timedelta(minutes=60)
    rows = list(
        APIAuditLog.objects.filter(timestamp__gte=start).values("timestamp", "status_code", "duration_ms")
    )
    buckets = {}
    for r in rows:
        t = r["timestamp"].replace(second=0, microsecond=0)
        b = buckets.setdefault(t, {"req": 0, "err": 0, "dur": []})
        b["req"] += 1
        if int(r["status_code"] or 0) >= 400:
            b["err"] += 1
        if r["duration_ms"] is not None:
            b["dur"].append(int(r["duration_ms"]))
    timestamps = []
    req = []
    err_rate = []
    avg_ms = []
    p95_ms = []
    slo_pct = []
    for i in range(60):
        ts = start.replace(second=0, microsecond=0) + timedelta(minutes=i)
        b = buckets.get(ts, {"req": 0, "err": 0, "dur": []})
        timestamps.append(ts.isoformat())
        req.append(b["req"])
        er = (b["err"] / b["req"] * 100) if b["req"] > 0 else 0
        err_rate.append(round(er, 2))
        if b["dur"]:
            avg = sum(b["dur"]) / len(b["dur"])
            avg_ms.append(round(avg, 2))
            s = sorted(b["dur"])
            k = max(int(0.95 * (len(s) - 1)), 0)
            p95_ms.append(float(s[k]))
            ok = sum(1 for x in b["dur"] if x <= 2000)
            slo = ok / len(b["dur"]) * 100
            slo_pct.append(round(slo, 2))
        else:
            avg_ms.append(0)
            p95_ms.append(0)
            slo_pct.append(100)
    return JsonResponse(
        {
            "timestamps": timestamps,
            "requests_per_min": req,
            "error_rate_percent": err_rate,
            "avg_ms": avg_ms,
            "p95_ms": p95_ms,
            "slo_under_2s_percent": slo_pct,
        }
    )


def metrics_top_endpoints_data(request):
    now = timezone.now()
    start = now - timedelta(days=1)
    vol = (
        APIAuditLog.objects.filter(timestamp__gte=start)
        .values("endpoint")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )
    err = (
        APIAuditLog.objects.filter(timestamp__gte=start, status_code__gte=400)
        .values("endpoint")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )
    return JsonResponse(
        {
            "top_volume": [{"endpoint": r["endpoint"], "count": r["count"]} for r in vol],
            "top_errors": [{"endpoint": r["endpoint"], "count": r["count"]} for r in err],
        }
    )


def metrics_rate_limit_data(request):
    now = timezone.now()
    start = now - timedelta(days=1)
    qs = (
        APIAuditLog.objects.filter(timestamp__gte=start, status_code=429)
        .values("api_key__key")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    data = {row["api_key__key"] or "": row["count"] for row in qs}
    return JsonResponse({"rate_limited_by_api_key": data})
