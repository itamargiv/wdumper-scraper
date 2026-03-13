from typing import Any

from wdumper_scraper.dump_info_page import DumpInfoPage

__all__ = ['DumpInfo']

class DumpInfo:
    def __init__(self, page: DumpInfoPage):
        self.__page = page
        self.__spec = self.__page.extract_spec()
        self.__data = {
            "id": page.dump_id,
            "name": page.extract_name(),
            "url": page.url,
            **self.__map_filters()
        }

    @property
    def data(self) -> dict[str, Any]:
        return self.__data

    def __map_filters(self) -> dict[str, str]:
        if not self.__spec:
            return {}

        filter_keys = ["labels", "descriptions", "aliases", "sitelinks"]

        return {
            key: 'yes' if self.__spec[key] else 'no' for key in filter_keys
        }

