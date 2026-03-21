from collections.abc import Callable

import pytest
from pytest_mock import MockerFixture
from requests.exceptions import RequestException

from wdumper_scraper import Scraper, ScraperError


def test_scrape_parses_html(make_scraper: Callable[..., Scraper]) -> None:
    scraper = make_scraper(body="<p>hello</p>")
    result = scraper.scrape("http://example.com")
    tag = result.find("p")
    assert tag is not None
    assert tag.text == "hello"


def test_scrape_raises_scraper_error_on_bad_status(
    make_scraper: Callable[..., Scraper],
) -> None:
    scraper = make_scraper(status_code=404)
    with pytest.raises(ScraperError, match="404"):
        scraper.scrape("http://example.com")


def test_scrape_raises_scraper_error_on_connection_error(
    make_scraper: Callable[..., Scraper], mocker: MockerFixture
) -> None:
    scraper = make_scraper()
    mocker.patch.object(
        scraper._Scraper__session,  # type: ignore[attr-defined]
        "get",
        side_effect=RequestException("connection refused"),
    )
    with pytest.raises(ScraperError, match="connection refused"):
        scraper.scrape("http://example.com")
