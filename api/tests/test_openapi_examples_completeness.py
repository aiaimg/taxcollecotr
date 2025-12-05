from django.test import TestCase
from rest_framework.test import APIClient


class OpenAPIExamplesCompletenessTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_all_operations_have_examples(self):
        resp = self.client.get("/api/schema/", HTTP_ACCEPT="application/json")
        self.assertEqual(resp.status_code, 200)
        import json
        schema = json.loads(resp.content)
        paths = schema.get("paths", {})
        missing = []
        for path, ops in paths.items():
            for method, op in ops.items():
                if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                    continue
                has_examples = False
                # request examples
                rb = op.get("requestBody") or {}
                for ct, entry in (rb.get("content") or {}).items():
                    if entry.get("examples"):
                        has_examples = True
                        break
                # response examples
                if not has_examples:
                    for status, rentry in (op.get("responses") or {}).items():
                        content = rentry.get("content") or {}
                        for ct, centry in content.items():
                            if centry.get("examples"):
                                has_examples = True
                                break
                        if has_examples:
                            break
                # vendor code samples
                if not has_examples and op.get("x-codeSamples"):
                    has_examples = True
                if not has_examples:
                    missing.append((path, method))
        self.assertEqual(missing, [], f"Missing examples for operations: {missing}")
