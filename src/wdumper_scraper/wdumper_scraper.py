import logging
from importlib.metadata import version

from requests_ratelimiter import SQLiteBucket  # type: ignore[attr-defined]

from wdumper_scraper.cached_limiter_session import CachedLimiterSession
from wdumper_scraper.dumps_info_loader import DumpsInfoLoader
from wdumper_scraper.scrape_reporter import NullReporter, ScrapeReporter
from wdumper_scraper.scrape_result import ScrapeResult
from wdumper_scraper.scraper import Scraper
from wdumper_scraper.wdumper_client import WDumperClient

__all__ = ["WDumperScraper"]

_PACKAGE_NAME = "wdumper-scraper"
_REPO_URL = "https://github.com/wdumper/wdumper-scraper"


class WDumperScraper:
    def __init__(
        self,
        cache_path: str = ".",
        user_agent: str | None = None,
        max_workers: int = 5,
        max_retries: int = 0,
        retry_delay: int = 5,
        timeout: int = 10,
        per_second: int = 10,
        read_only: bool = False,
        last_id: int = 0,
        debug: bool = False,
    ) -> None:
        if not user_agent:
            pkg_version = version(_PACKAGE_NAME)
            user_agent = f"{_PACKAGE_NAME}/{pkg_version} ({_REPO_URL})"

        self.__user_agent = user_agent
        self.__timeout = timeout
        self.__cache_path = cache_path
        self.__per_second = per_second
        self.__max_workers = max_workers
        self.__max_retries = 0 if read_only else max_retries
        self.__retry_delay = retry_delay
        self.__read_only = read_only
        self.__last_id = 100 if read_only and last_id < 1 else last_id
        self.__debug = debug
        self.__reporter = self.__make_reporter()
        self.__loader = self.__make_loader()

    def __make_session(self) -> CachedLimiterSession:
        cache_path = self.__cache_path

        return CachedLimiterSession(
            user_agent=self.__user_agent,
            timeout=self.__timeout,
            cache_name=f"{cache_path}/cache/scraper_cache",
            backend="sqlite",
            read_only=self.__read_only,
            only_if_cached=self.__read_only,
            ignored_parameters=["Accept-Encoding"],
            bucket_class=SQLiteBucket,
            per_second=self.__per_second,
            bucket_kwargs={
                "path": f"{cache_path}/cache/ratelimiter.sqlite",
                "isolation_level": "EXCLUSIVE",
                "check_same_thread": False,
            },
        )

    def __make_reporter(self) -> NullReporter:
        if self.__debug:
            package_logger = logging.getLogger("wdumper_scraper")
            if not package_logger.handlers:
                handler = logging.StreamHandler()
                handler.setLevel(logging.DEBUG)
                package_logger.addHandler(handler)
            package_logger.setLevel(logging.DEBUG)
            return NullReporter()

        return ScrapeReporter()

    def __make_loader(self) -> DumpsInfoLoader:
        session = self.__make_session()
        scraper = Scraper(session)
        wdumper_client = WDumperClient(session)
        return DumpsInfoLoader(
            scraper, wdumper_client, self.__max_workers, self.__reporter
        )

    def run(self) -> ScrapeResult:
        result = self.__loader.scrape(
            max_retries=self.__max_retries,
            retry_delay=self.__retry_delay,
            last_id=self.__last_id,
        )

        self.__reporter.report(result)
        return result
