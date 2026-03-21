from wdumper_scraper.exceptions import PageError
from wdumper_scraper.scraper import Scraper

__all__ = ["RecentDumpsPage"]


class RecentDumpsPage:
    def __init__(self, scraper: Scraper) -> None:
        self.__url = "https://wdumps.toolforge.org/dumps"
        self.__soup = scraper.scrape(self.__url)

    def extract_last_id(self) -> int:
        try:
            table = self.__soup.find("table")
            a_tag = table.find("a") if table else None
            href = str(a_tag["href"]) if a_tag else None
            dump_id = href.split("/")[-1] if href else None
            return int(dump_id)  # type: ignore[arg-type]
        except (AttributeError, TypeError, KeyError, ValueError) as e:
            raise PageError(str(e)) from e
