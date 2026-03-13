import json

from wdumper_scraper.scraper import Scraper, CacheDuration

__all__ = ['DumpInfoPage']

class DumpInfoPage:
    def __init__(
            self,
            scraper: Scraper,
            dump_id: int,
            cache_duration: CacheDuration = CacheDuration.NO_CACHE
    ) -> None:
        self.__dump_id = dump_id
        self.__url = f"https://wdumps.toolforge.org/dump/{dump_id}"
        self.__soup = scraper.scrape(self.__url, cache_duration)

    @property
    def dump_id(self) -> int:
        return self.__dump_id

    @property
    def url(self) -> str:
        return self.__url

    def extract_name(self) -> str:
        heading = self.__soup.find("h2")

        return heading.get_text(strip = True) if heading else ""

    def extract_spec(self) -> dict | None:
        # noinspection PyTypeChecker
        heading = self.__soup.find("h2", string="Spec")
        pre = heading.find_next("pre") if heading else None
        content = pre.get_text(strip = True) if pre else None

        return json.loads(content) if content else None
