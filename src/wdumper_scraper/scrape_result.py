from typing import NamedTuple, Any

__all__ = ["ScrapeResult"]

class ScrapeResult(NamedTuple):
    dumps: list[dict[str, Any]]
    skipped: list[dict[str, Any]]