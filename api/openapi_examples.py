def example_request_for(path: str, method: str):
    method = method.upper()
    if "/auth/login" in path and method == "POST":
        return {
            "application/json": {
                "email": "agent@example.com",
                "password": "stringPassword123",
            }
        }
    if "/vehicles" in path and method in {"POST", "PUT", "PATCH"}:
        return {
            "application/json": {
                "plaque": "1234ABC",
                "categorie": "A",
                "marque": "Toyota",
                "modele": "Corolla",
                "annee": 2018,
            }
        }
    return {
        "application/json": {"example": "value"}
    }


def example_response_for(path: str, method: str, status: str):
    if "/auth/login" in path and status == "200":
        return {
            "application/json": {
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }
    if "/health" in path and status == "200":
        return {
            "application/json": {"status": "ok", "timestamp": "2025-01-01T00:00:00Z"}
        }
    return {
        "application/json": {"result": "ok"}
    }


def code_samples_for(path: str, method: str):
    url = "http://localhost:8000" + path
    samples = [
        {
            "lang": "cURL",
            "label": "cURL",
            "source": f"curl -X {method.upper()} '{url}' -H 'Authorization: Bearer <token>' -H 'Content-Type: application/json'",
        },
        {
            "lang": "Python",
            "label": "Python (requests)",
            "source": (
                "import requests\n"
                f"resp = requests.{method.lower()}('{url}', headers={{'Authorization': 'Bearer <token>'}}, json={{}})\n"
                "print(resp.status_code)"
            ),
        },
        {
            "lang": "JavaScript",
            "label": "JavaScript (fetch)",
            "source": (
                "fetch('" + url + "', {method: '" + method.upper() + "', headers: {Authorization: 'Bearer <token>', 'Content-Type': 'application/json'}, body: JSON.stringify({})}).then(r => r.json()).then(console.log)"
            ),
        },
    ]
    return samples

