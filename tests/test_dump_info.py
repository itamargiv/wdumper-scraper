from wdumper_scraper.dump_info import DumpInfo
from wdumper_scraper.wdumper_client import Dump

DUMP_ID = 1
TITLE = "My Dump"
URL = "https://wdumps.toolforge.org/dump/1"


def make_dump(
    labels: bool = True,
    descriptions: bool = True,
    aliases: bool = True,
    sitelinks: bool = True,
) -> Dump:
    return {
        "id": DUMP_ID,
        "title": TITLE,
        "spec": {
            "languages": None,
            "labels": labels,
            "descriptions": descriptions,
            "aliases": aliases,
            "sitelinks": sitelinks,
        },
    }


def test_data_contains_correct_id() -> None:
    info = DumpInfo(URL, make_dump())
    assert info.data["id"] == DUMP_ID


def test_data_maps_title_to_name() -> None:
    info = DumpInfo(URL, make_dump())
    assert info.data["name"] == TITLE


def test_data_contains_url() -> None:
    info = DumpInfo(URL, make_dump())
    assert info.data["url"] == URL


def test_data_contains_all_filter_keys() -> None:
    info = DumpInfo(URL, make_dump())
    assert {"labels", "descriptions", "aliases", "sitelinks"}.issubset(
        info.data.keys()
    )


def test_true_filter_maps_to_yes() -> None:
    info = DumpInfo(
        URL,
        make_dump(labels=True, descriptions=True, aliases=True, sitelinks=True),
    )
    assert all(
        info.data[key] == "yes"
        for key in ["labels", "descriptions", "aliases", "sitelinks"]
    )


def test_false_filter_maps_to_no() -> None:
    info = DumpInfo(
        URL,
        make_dump(
            labels=False, descriptions=False, aliases=False, sitelinks=False
        ),
    )
    assert all(
        info.data[key] == "no"
        for key in ["labels", "descriptions", "aliases", "sitelinks"]
    )
