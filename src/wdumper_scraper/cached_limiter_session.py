from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin

__all__ = ["CachedLimiterSession"]

class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    def __init__(self, *args, user_agent: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_agent is not None:
            self.headers.update({"User-Agent": user_agent})
