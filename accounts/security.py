from django.conf import settings
from django.core.cache import cache


def _failure_key(email: str, ip: str) -> str:
    normalized_email = (email or "").strip().lower()
    normalized_ip = (ip or "unknown").strip()
    return f"auth:fail:{normalized_email}:{normalized_ip}"


def _lock_key(email: str, ip: str) -> str:
    normalized_email = (email or "").strip().lower()
    normalized_ip = (ip or "unknown").strip()
    return f"auth:lock:{normalized_email}:{normalized_ip}"


def is_login_locked(email: str, ip: str) -> bool:
    return bool(cache.get(_lock_key(email, ip)))


def record_failed_login(email: str, ip: str) -> None:
    key = _failure_key(email, ip)
    lock_key = _lock_key(email, ip)
    max_attempts = int(getattr(settings, "AUTH_MAX_FAILED_ATTEMPTS", 5))
    window_seconds = int(getattr(settings, "AUTH_FAILURE_WINDOW_SECONDS", 600))
    lock_seconds = int(getattr(settings, "AUTH_LOCKOUT_SECONDS", 900))

    failures = int(cache.get(key, 0)) + 1
    cache.set(key, failures, timeout=window_seconds)

    if failures >= max_attempts:
        cache.set(lock_key, True, timeout=lock_seconds)


def clear_failed_logins(email: str, ip: str) -> None:
    cache.delete(_failure_key(email, ip))
    cache.delete(_lock_key(email, ip))
