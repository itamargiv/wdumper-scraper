import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import NamedTuple, Any
from wdumper_scraper.dump_info import DumpInfo
from wdumper_scraper.dump_page import DumpPage
from wdumper_scraper.exceptions import WDumperError
from wdumper_scraper.recent_dumps_page import RecentDumpsPage
from wdumper_scraper.scraper import CacheDuration, Scraper

__all__ = ["DumpsInfoLoader", "ScrapeResult"]

class ScrapeResult(NamedTuple):
    dumps: list[dict[str, Any]]
    skipped: list[dict[str, Any]]

class DumpsInfoLoader:
    def __init__(self, scraper: Scraper, max_workers: int = 5) -> None:
        self.__scraper = scraper
        self.__max_workers = max_workers

    def __scrape_dump(self, last_id: int, dump_id: int) -> DumpInfo:
        cache_duration = (
            CacheDuration.INDEFINITE
            if dump_id < last_id - 10
            else CacheDuration.SHORT
        )
        dump_page = DumpPage(self.__scraper, dump_id, cache_duration)
        return DumpInfo(dump_page)

    def __scrape_ids(self, last_id: int, ids) -> ScrapeResult:
        dumps = []
        skipped = []

        with ThreadPoolExecutor(max_workers=self.__max_workers) as executor:
            futures = {
                executor.submit(self.__scrape_dump, last_id, i): i
                for i in ids
            }

            for future in as_completed(futures):
                dump_id = futures[future]

                try:
                    dump_info = future.result()
                except WDumperError as e:
                    skipped.append({"id": dump_id, "error": str(e)})
                else:
                    dumps.append(dump_info.data)

        return ScrapeResult(
            dumps=sorted(dumps, key=lambda d: d["id"], reverse=True),
            skipped=sorted(skipped, key=lambda s: s["id"], reverse=True),
        )

    def scrape(self, max_retries: int = 0, retry_delay: float = 5.0) -> ScrapeResult:
        last_id = RecentDumpsPage(self.__scraper).extract_last_id()
        result = self.__scrape_ids(last_id, range(last_id, 0, -1))
        all_dumps = list(result.dumps)

        for _ in range(max_retries):
            if not result.skipped:
                break
            time.sleep(retry_delay)
            retry_ids = [entry["id"] for entry in result.skipped]
            result = self.__scrape_ids(last_id, retry_ids)
            all_dumps.extend(result.dumps)

        return ScrapeResult(
            dumps=sorted(all_dumps, key=lambda d: d["id"], reverse=True),
            skipped=result.skipped,
        )
