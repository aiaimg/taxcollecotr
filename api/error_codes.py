from typing import Dict

ERROR_CODES: Dict[str, Dict] = {
    "validation_error": {
        "http_status": 400,
        "type": "/errors/validation_error",
        "titles": {
            "fr": "Erreur de validation",
            "mg": "Hadisoana fanamarinana",
            "en": "Validation Error",
        },
    },
    "authentication_error": {
        "http_status": 401,
        "type": "/errors/authentication_error",
        "titles": {
            "fr": "Authentification requise",
            "mg": "Tsy nahomby ny fankatoavana",
            "en": "Authentication Required",
        },
    },
    "permission_denied": {
        "http_status": 403,
        "type": "/errors/permission_denied",
        "titles": {
            "fr": "Accès refusé",
            "mg": "Tsy azo idirana",
            "en": "Access Denied",
        },
    },
    "not_found": {
        "http_status": 404,
        "type": "/errors/not_found",
        "titles": {
            "fr": "Ressource introuvable",
            "mg": "Tsy hita ny loharano",
            "en": "Resource Not Found",
        },
    },
    "rate_limit": {
        "http_status": 429,
        "type": "/errors/rate_limit",
        "titles": {
            "fr": "Limite de requêtes dépassée",
            "mg": "Be loatra ny fangatahana",
            "en": "Rate Limit Exceeded",
        },
    },
    "bad_request": {
        "http_status": 400,
        "type": "/errors/bad_request",
        "titles": {
            "fr": "Requête invalide",
            "mg": "Fangatahana diso",
            "en": "Bad Request",
        },
    },
    "internal_error": {
        "http_status": 500,
        "type": "/errors/internal_error",
        "titles": {
            "fr": "Erreur interne du serveur",
            "mg": "Hadisoana anatiny amin'ny lohamilina",
            "en": "Internal Server Error",
        },
    },
    "error": {
        "http_status": 400,
        "type": "/errors/error",
        "titles": {
            "fr": "Erreur",
            "mg": "Hadisoana",
            "en": "Error",
        },
    },
}


def get_error_info(code: str, lang: str = "fr") -> Dict:
    info = ERROR_CODES.get(code) or ERROR_CODES["error"]
    title = info["titles"].get(lang) or info["titles"].get("fr") or next(iter(info["titles"].values()))
    return {"http_status": info["http_status"], "type": info["type"], "title": title}

