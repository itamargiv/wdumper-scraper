import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from wdumper_scraper.dump_info import DumpInfo
from wdumper_scraper.exceptions import WDumperError
from wdumper_scraper.recent_dumps_page import RecentDumpsPage
from wdumper_scraper.scrape_result import ScrapeResult
from wdumper_scraper.scraper import CacheDuration
from wdumper_scraper.scrape_reporter import NullReporter
from wdumper_scraper.wdumper_clients import WDumperClients


__all__ = ["DumpsInfoLoader"]


class DumpsInfoLoader:
    def __init__(self, clients: WDumperClients, max_workers: int = 5, reporter: NullReporter = NullReporter()) -> None:
        self.__scraper = clients.scraper
        self.__wdumper = clients.wdumper
        self.__max_workers = max_workers
        self.__reporter = reporter


    def __get_dump(self, last_id: int, dump_id: int) -> DumpInfo:
        cache_duration = (
            CacheDuration.INDEFINITE
            if dump_id < last_id - 10
            else CacheDuration.SHORT
        )

        url, dump = self.__wdumper.get_dump(dump_id, cache_duration)
        return DumpInfo(url, dump)

    def __scrape_ids(self, last_id: int, ids, title: str = "Scraping") -> ScrapeResult:
        dumps = []
        skipped = []

        with ThreadPoolExecutor(max_workers=self.__max_workers) as executor:
            futures = {
                executor.submit(self.__get_dump, last_id, i): i
                for i in ids
            }

            progress_bar = self.__reporter.scrape_bar(as_completed(futures), total=len(futures), desc=title)

            for future in progress_bar:
                dump_id = futures[future]

                try:
                    dump_info = future.result()
                except WDumperError as e:
                    skipped.append({"id": dump_id, "error": str(e)})
                else:
                    dumps.append(dump_info.data)

                progress_bar.set_postfix(scraped = len(dumps), skipped = len(skipped))

            progress_bar.close()

        return ScrapeResult(
            dumps=sorted(dumps, key=lambda d: d["id"], reverse=True),
            skipped=sorted(skipped, key=lambda s: s["id"], reverse=True),
        )

    def scrape(self, max_retries: int = 0, retry_delay: float = 5.0) -> ScrapeResult:
        last_id = RecentDumpsPage(self.__scraper).extract_last_id()
        result = self.__scrape_ids(last_id, range(last_id, 0, -1))
        all_dumps = list(result.dumps)

        for n in range(1, max_retries + 1):
            if not result.skipped:
                break

            self.__reporter.countdown(math.ceil(retry_delay), n, max_retries)

            retry_ids = [entry["id"] for entry in result.skipped]
            result = self.__scrape_ids(last_id, retry_ids, f"Retrying (attempt {n}/{max_retries})")
            all_dumps.extend(result.dumps)

        return ScrapeResult(
            dumps=sorted(all_dumps, key=lambda d: d["id"], reverse=True),
            skipped=result.skipped,
        )
