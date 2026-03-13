import pytest
from wdumper_scraper import DumpInfo

DUMP_ID = 42
DUMP_NAME = "My Dump"
DUMP_URL = f"https://wdumps.toolforge.org/dump/{DUMP_ID}"
MIXED_SPEC = {
    "labels": True,
    "descriptions": True,
    "aliases": False,
    "sitelinks": False,
}


@pytest.fixture
def make_page(mocker):
    def factory(dump_id=DUMP_ID, name=DUMP_NAME, url=DUMP_URL, spec=MIXED_SPEC):
        page = mocker.MagicMock()
        page.dump_id = dump_id
        page.url = url
        page.extract_name.return_value = name
        page.extract_spec.return_value = spec
        return page

    return factory


def test_data_contains_id(make_page):
    page = make_page()
    assert DumpInfo(page).data["id"] == DUMP_ID


def test_data_contains_name(make_page):
    page = make_page()
    assert DumpInfo(page).data["name"] == DUMP_NAME


def test_data_contains_url(make_page):
    page = make_page()
    assert DumpInfo(page).data["url"] == DUMP_URL


def test_data_maps_all_filters(make_page):
    page = make_page(spec=MIXED_SPEC)
    assert DumpInfo(page).data == {
        "id": DUMP_ID,
        "name": DUMP_NAME,
        "url": DUMP_URL,
        "labels": "yes",
        "descriptions": "yes",
        "aliases": "no",
        "sitelinks": "no",
    }


def test_data_has_no_filter_keys_when_spec_is_none(make_page):
    page = make_page(spec=None)
    assert DumpInfo(page).data == {
        "id": DUMP_ID,
        "name": DUMP_NAME,
        "url": DUMP_URL,
    }

