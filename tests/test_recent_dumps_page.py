from collections.abc import Callable

import pytest
from pytest_mock import MockerFixture

from wdumper_scraper.exceptions import PageError, ScraperError
from wdumper_scraper.recent_dumps_page import RecentDumpsPage
from wdumper_scraper.scraper import Scraper

SINGLE_ROW_HTML = (
    '<table><tr><td><a href="/dump/42">Dump 42</a></td></tr></table>'
)
MULTI_ROW_HTML = """
<table>
  <tr>
    <td><a href="/dump/42">Dump 42</a></td>
  </tr>
  <tr>
    <td><a href="/dump/99">Dump 99</a></td>
  </tr>
</table>'
"""
EMPTY_TABLE_HTML = "<table></table>"
NO_HREF_HTML = "<table><tr><td><a>No href</a></td></tr></table>"
NON_INTEGER_ID_HTML = (
    '<table><tr><td><a href="/dump/abc">Dump abc</a></td></tr></table>'
)
NO_TABLE_HTML = "<p>some content</p>"


def test_scrape_called_with_correct_url(
    make_scraper: Callable[..., Scraper], mocker: MockerFixture
) -> None:
    scraper = make_scraper(body=SINGLE_ROW_HTML)
    mocker.spy(scraper, "scrape")
    RecentDumpsPage(scraper)
    scraper.scrape.assert_called_once_with("https://wdumps.toolforge.org/dumps")  # type: ignore[attr-defined]


def test_extract_last_id_returns_correct_id(
    make_scraper: Callable[..., Scraper],
) -> None:
    scraper = make_scraper(body=SINGLE_ROW_HTML)
    page = RecentDumpsPage(scraper)
    assert page.extract_last_id() == 42


def test_extract_last_id_returns_first_row_id(
    make_scraper: Callable[..., Scraper],
) -> None:
    scraper = make_scraper(body=MULTI_ROW_HTML)
    page = RecentDumpsPage(scraper)
    assert page.extract_last_id() == 42


def test_extract_last_id_raises_page_error_on_missing_table(
    make_scraper: Callable[..., Scraper],
) -> None:
    scraper = make_scraper(body=NO_TABLE_HTML)
    page = RecentDumpsPage(scraper)
    with pytest.raises(PageError):
        page.extract_last_id()


def test_extract_last_id_raises_page_error_on_missing_link(
    make_scraper: Callable[..., Scraper],
) -> None:
    scraper = make_scraper(body=EMPTY_TABLE_HTML)
    page = RecentDumpsPage(scraper)
    with pytest.raises(PageError):
        page.extract_last_id()


def test_extract_last_id_raises_page_error_on_missing_href(
    make_scraper: Callable[..., Scraper],
) -> None:
    scraper = make_scraper(body=NO_HREF_HTML)
    page = RecentDumpsPage(scraper)
    with pytest.raises(PageError):
        page.extract_last_id()


def test_extract_last_id_raises_page_error_on_non_integer_id(
    make_scraper: Callable[..., Scraper],
) -> None:
    scraper = make_scraper(body=NON_INTEGER_ID_HTML)
    page = RecentDumpsPage(scraper)
    with pytest.raises(PageError):
        page.extract_last_id()


def test_init_raises_scraper_error_on_bad_status(
    make_scraper: Callable[..., Scraper],
) -> None:
    scraper = make_scraper(status_code=404)
    with pytest.raises(ScraperError):
        RecentDumpsPage(scraper)
