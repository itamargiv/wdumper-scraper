from Scraper import Scraper

class RecentDumpsPage:
    def __init__(self, scraper: Scraper) -> None:
        self.__url = "https://wdumps.toolforge.org/dumps"
        self.__soup = scraper.scrape(self.__url)

    def extract_last_id(self) -> int:
        dump_id = self.__soup.find("table").find("a")["href"].split("/")[-1]

        return int(dump_id)
