from typing import Any, NamedTuple

__all__ = ["ScrapeResult"]


class ScrapeResult(NamedTuple):
    dumps: list[dict[str, Any]]
    skipped: list[dict[str, Any]]
