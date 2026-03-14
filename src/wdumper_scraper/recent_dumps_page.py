from wdumper_scraper.exceptions import PageError
from wdumper_scraper.scraper import Scraper

__all__ = ['RecentDumpsPage']


class RecentDumpsPage:
    def __init__(self, scraper: Scraper) -> None:
        self.__url = "https://wdumps.toolforge.org/dumps"
        self.__soup = scraper.scrape(self.__url)

    def extract_last_id(self) -> int:
        try:
            dump_id = self.__soup.find("table").find("a")["href"].split("/")[-1]
            return int(dump_id)
        except (AttributeError, TypeError, KeyError, ValueError) as e:
            raise PageError(str(e)) from e

