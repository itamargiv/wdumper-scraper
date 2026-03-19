import json
import logging
from typing import TypedDict, Any

from requests import RequestException

from wdumper_scraper.scraper import CacheDuration
from wdumper_scraper.cached_limiter_session import CachedLimiterSession
from wdumper_scraper.exceptions import ClientError

logger = logging.getLogger(__name__)
__all__ = ["WDumperClient", "Dump"]

class DumpSpec(TypedDict):
    labels: bool
    descriptions: bool
    aliases: bool
    sitelinks: bool

class Dump(TypedDict):
    id: int
    title: str
    spec: DumpSpec

class WDumperClient:
    def __init__(self, session: CachedLimiterSession) -> None:
        self.__session = session
        self.__base_url = "https://wdumps.toolforge.org"

    def __get(
            self,
            url: str,
            cache_duration: CacheDuration
    ) -> Any:
        try:
            response = self.__session.get(
                url,
                headers = {'Accept': 'application/json'},
                expire_after=cache_duration.value
            )
        except RequestException as e:
            raise ClientError(str(e)) from e

        logger.debug(f"Cache {'HIT' if response.from_cache else 'MISS'} for URL: {url}")

        if response.status_code != 200:
            raise ClientError(f"Status Code: {response.status_code}")

        try:
            return response.json()
        except json.decoder.JSONDecodeError as e:
            raise ClientError(f"Error parsing JSON: {e}")

    def get_dump(self, dump_id: int, cache_duration: CacheDuration = CacheDuration.NO_CACHE) -> tuple[str, Dump]:
        url = f"{self.__base_url}/dump/{dump_id}"
        response_data = self.__get(url, cache_duration)
        dump = response_data["dump"]

        try:
            if isinstance(dump.get("spec"), str):
                dump["spec"] = json.loads(dump["spec"])
        except json.decoder.JSONDecodeError as e:
            raise ClientError(f"Error parsing JSON: {e}")

        return url, dump