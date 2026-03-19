import logging
from wdumper_scraper.cached_limiter_session import CachedLimiterSession
from wdumper_scraper.scraper import Scraper
from wdumper_scraper.wdumper_client import WDumperClient

__all__ = ["WDumperClients"]


class WDumperClients:
    def __init__(self, session: CachedLimiterSession, debug: bool = False) -> None:
        self.__scraper = Scraper(session)
        self.__wdumper = WDumperClient(session)

        if debug:
            package_logger = logging.getLogger("wdumper_scraper")
            if not package_logger.handlers:
                handler = logging.StreamHandler()
                handler.setLevel(logging.DEBUG)
                package_logger.addHandler(handler)
            package_logger.setLevel(logging.DEBUG)

    @property
    def scraper(self) -> Scraper:
        return self.__scraper

    @property
    def wdumper(self) -> WDumperClient:
        return self.__wdumper

