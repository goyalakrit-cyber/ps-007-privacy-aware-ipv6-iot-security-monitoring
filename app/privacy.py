import hashlib
import hmac
from ipaddress import ip_address


def stable_device_key(device_id: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), device_id.encode("utf-8"), hashlib.sha256).hexdigest()


def hash_identifier(value: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), value.strip().encode("utf-8"), hashlib.sha256).hexdigest()


def redact_ipv6(ipv6: str) -> str:
    try:
        addr = ip_address(ipv6)
    except ValueError:
        return "invalid"
    if addr.version != 6:
        return "invalid"
    parts = str(addr).split(":")
    if len(parts) < 8:
        return ":".join(parts[:4]) + ":xxxx:xxxx:xxxx:xxxx"
    return ":".join(parts[:4]) + ":xxxx:xxxx:xxxx:xxxx"


def format_alert_payload(device_key: str, severity: str, title: str, description: str, score: float) -> dict:
    return {
        "device_key": device_key,
        "severity": severity,
        "title": title,
        "description": description,
        "score": float(score),
    }
