from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import NamedTuple
from wdumper_scraper.dump_info import DumpInfo
from wdumper_scraper.dump_info_page import DumpInfoPage
from wdumper_scraper.recent_dumps_page import RecentDumpsPage
from wdumper_scraper.scraper import CacheDuration, Scraper

__all__ = ["DumpsInfoLoader", "ScrapeResult"]

class ScrapeResult(NamedTuple):
    dumps: list[DumpInfo] = []
    skipped: list[dict] = []

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
        dump_info_page = DumpInfoPage(self.__scraper, dump_id, cache_duration)
        return DumpInfo(dump_info_page)

    def scrape(self) -> ScrapeResult:
        results = ScrapeResult(dumps=[], skipped=[])

        last_id = RecentDumpsPage(self.__scraper).extract_last_id()

        with (ThreadPoolExecutor(max_workers=self.__max_workers) as executor):
            futures = {
                executor.submit(self.__scrape_dump, last_id, i): i
                for i in range(last_id, 0, -1)
            }

            for future in as_completed(futures):
                dump_id = futures[future]

                try:
                    dump_info = future.result()
                except Exception as e:
                    results.skipped.append({"id": dump_id, "error": str(e)})
                else:
                    results.dumps.append(dump_info.data)

        return results
