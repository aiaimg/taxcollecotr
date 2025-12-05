import re


SENSITIVE_KEYS = {
    'nif', 'numero_nif', 'tax_id',
    'phone', 'telephone', 'mobile', 'tel',
    'email', 'mail',
    'password', 'pass', 'mot_de_passe', 'pwd',
}


def mask_nif(value: str) -> str:
    s = re.sub(r"\D", "", str(value))
    if len(s) <= 5:
        return "*" * len(s)
    return "*" * (len(s) - 5) + s[-5:]


def mask_phone(value: str) -> str:
    digits = re.sub(r"\D", "", str(value))
    if len(digits) <= 4:
        return "*" * len(digits)
    masked = "*" * (len(digits) - 4) + digits[-4:]
    return masked


def mask_email(value: str) -> str:
    v = str(value)
    if "@" not in v:
        return "***"
    local, domain = v.split("@", 1)
    if len(local) <= 2:
        local_masked = "*" * len(local)
    else:
        local_masked = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{local_masked}@{domain}"


def mask_password(value: str) -> str:
    return "********"


def mask_value(key: str, value):
    k = key.lower()
    if k in {"nif", "numero_nif", "tax_id"}:
        return mask_nif(value)
    if k in {"phone", "telephone", "mobile", "tel"}:
        return mask_phone(value)
    if k in {"email", "mail"}:
        return mask_email(value)
    if k in {"password", "pass", "mot_de_passe", "pwd"}:
        return mask_password(value)
    return value


def mask_payload(data):
    if isinstance(data, dict):
        return {k: mask_value(k, mask_payload(v)) if k.lower() in SENSITIVE_KEYS else mask_payload(v) for k, v in data.items()}
    if isinstance(data, list):
        return [mask_payload(v) for v in data]
    return data
