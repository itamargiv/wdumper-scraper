from typing import Literal

from wdumper_scraper.wdumper_client import Dump

__all__ = ["DumpInfo"]

FilterKey = Literal["labels", "descriptions", "aliases", "sitelinks"]


class DumpInfo:
    def __init__(self, url: str, dump: Dump) -> None:
        self.__dump = dump
        self.__spec = dump["spec"]
        self.__data: dict[str, str | int] = {
            "id": dump["id"],
            "name": dump["title"],
            "url": url,
            "languages": self.__map_languages(),
            **self.__map_filters(),
        }

    @property
    def data(self) -> dict[str, str | int]:
        return self.__data

    def __map_filters(self) -> dict[str, str]:
        filter_keys: list[FilterKey] = [
            "labels",
            "descriptions",
            "aliases",
            "sitelinks",
        ]

        return {key: "yes" if self.__spec[key] else "no" for key in filter_keys}

    def __map_languages(self) -> str:
        return " | ".join(self.__spec.get("languages") or [])
