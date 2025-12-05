from django.test import RequestFactory
from django.http import JsonResponse
from django_prometheus.exports import ExportToDjangoView

from api.middleware.audit import AuditLoggingMiddleware


def test_prometheus_metrics_endpoint_records_requests_without_db(monkeypatch):
    rf = RequestFactory()
    req = rf.get("/api/v1/health/")
    mw = AuditLoggingMiddleware(get_response=lambda r: JsonResponse({}))

    class DummyModel:
        @staticmethod
        def objects_create(**kwargs):
            return None

    monkeypatch.setattr("api.middleware.audit.APIAuditLog", DummyModel)
    monkeypatch.setattr(DummyModel, "objects", type("O", (), {"create": DummyModel.objects_create}), raising=False)

    mw.process_request(req)
    resp = JsonResponse({})
    resp.status_code = 200
    mw.process_response(req, resp)

    m = ExportToDjangoView(req)
    assert m.status_code == 200
    body = m.content.decode("utf-8")
    assert "api_request_total" in body
    assert 'endpoint="/api/v1/health/"' in body
    assert 'method="GET"' in body
    assert 'status_code="200"' in body
