from typing import Dict
from api.openapi_examples import example_request_for, example_response_for, code_samples_for

from api.error_codes import ERROR_CODES


def add_problem_details_components(result: Dict, generator=None, request=None, public=None) -> Dict:
    components = result.setdefault("components", {}).setdefault("schemas", {})
    responses = result["components"].setdefault("responses", {})
    examples = result["components"].setdefault("examples", {})

    components["ProblemDetails"] = {
        "type": "object",
        "required": ["type", "title", "status"],
        "properties": {
            "type": {"type": "string", "format": "uri-reference"},
            "title": {"type": "string"},
            "status": {"type": "integer", "format": "int32"},
            "detail": {"type": "string"},
            "instance": {"type": "string", "format": "uri"},
            "code": {"type": "string"},
            "correlationId": {"type": "string"},
            "errors": {"type": "object"},
        },
        "description": "RFC 7807 Problem Details response",
    }

    responses["Problem"] = {
        "description": "Problem Details",
        "content": {
            "application/problem+json": {
                "schema": {"$ref": "#/components/schemas/ProblemDetails"},
            }
        },
    }

    for code, meta in ERROR_CODES.items():
        examples[f"problem_{code}"] = {
            "summary": code,
            "value": {
                "type": meta["type"],
                "title": meta["titles"].get("fr"),
                "status": meta["http_status"],
                "detail": "Exemple de message d'erreur",
                "instance": "/api/v1/example",
                "code": code,
                "correlationId": "abc123",
            },
        }

    paths = result.get("paths", {})
    for _, ops in paths.items():
        for method, op in ops.items():
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                op.setdefault("responses", {})
                for sc in ("400", "401", "403", "404", "429", "500"):
                    op["responses"].setdefault(sc, {"$ref": "#/components/responses/Problem"})
    return result


def add_examples_and_code_samples(result: Dict, generator=None, request=None, public=None) -> Dict:
    paths = result.get("paths", {})
    for path, ops in paths.items():
        for method, op in ops.items():
            m = method.lower()
            if m not in {"get", "post", "put", "patch", "delete"}:
                continue
            # Request examples
            if op.get("requestBody") is not None:
                rb = op.setdefault("requestBody", {})
                content = rb.setdefault("content", {})
                for ct, _schema in list(content.items()) or [("application/json", {})]:
                    req_example = example_request_for(path, m.upper())
                    if ct in req_example:
                        content[ct].setdefault("examples", {"default": {"value": req_example[ct]}})
            # Response examples
            responses = op.setdefault("responses", {})
            for status in list(responses.keys()) or ["200"]:
                resp_example = example_response_for(path, m.upper(), status)
                for ct, val in resp_example.items():
                    responses.setdefault(status, {"content": {}})
                    responses[status].setdefault("content", {})
                    responses[status]["content"].setdefault(ct, {})
                    responses[status]["content"][ct].setdefault("examples", {"default": {"value": val}})
            # Code samples vendor extension
            op.setdefault("x-codeSamples", code_samples_for(path, m.upper()))
            # Multilingual summaries (append FR/MG if summary exists)
            if "summary" in op and op["summary"]:
                op["description"] = op.get("description", op["summary"]) + "\n\nFR: " + op["summary"] + "\nMG: " + op["summary"]
    return result
