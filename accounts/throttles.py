from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        email = (request.data.get("email") if isinstance(request.data, dict) else "") or ""
        return self.cache_format % {
            "scope": self.scope,
            "ident": f"{ident}:{email.strip().lower()}",
        }


class AuthBurstRateThrottle(SimpleRateThrottle):
    scope = "auth_burst"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }
