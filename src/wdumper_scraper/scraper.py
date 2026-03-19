import logging
from enum import Enum
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

from wdumper_scraper.cached_limiter_session import CachedLimiterSession
from wdumper_scraper.exceptions import ScraperError

logger = logging.getLogger(__name__)
__all__ = ["Scraper", "CacheDuration"]

class CacheDuration(Enum):
    NO_CACHE = 0
    SHORT = 7200
    INDEFINITE = None

class Scraper:
    def __init__(self, session: CachedLimiterSession) -> None:
        self.__session = session

    def __get(
            self,
            url: str,
            cache_duration: CacheDuration
    ) -> str:
        try:
            response = self.__session.get(url, expire_after=cache_duration.value)
        except RequestException as e:
            raise ScraperError(str(e)) from e

        logger.debug(f"Cache {'HIT' if response.from_cache else 'MISS'} for URL: {url}")

        if response.status_code != 200:
            raise ScraperError(f"Status Code: {response.status_code}")

        return response.text

    def scrape(
            self,
            url: str,
            cache_duration: CacheDuration = CacheDuration.NO_CACHE
    ) -> BeautifulSoup:
        html = self.__get(url, cache_duration)
        return BeautifulSoup(html, "html.parser")
