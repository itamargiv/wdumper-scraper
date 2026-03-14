import pytest
from requests.exceptions import RequestException
from wdumper_scraper import ScraperError

def test_scrape_parses_html(make_scraper):
    scraper = make_scraper(body="<p>hello</p>")
    result = scraper.scrape("http://example.com")
    assert result.find("p").text == "hello"


def test_scrape_raises_scraper_error_on_bad_status(make_scraper):
    scraper = make_scraper(status_code=404)
    with pytest.raises(ScraperError, match="404"):
        scraper.scrape("http://example.com")


def test_scrape_raises_scraper_error_on_connection_error(make_scraper, mocker):
    scraper = make_scraper()
    mocker.patch.object(
        scraper._Scraper__session,
        "get",
        side_effect=RequestException("connection refused")
    )
    with pytest.raises(ScraperError, match="connection refused"):
        scraper.scrape("http://example.com")

