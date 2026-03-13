import pytest

def test_scrape_parses_html(make_scraper):
    scraper = make_scraper(body="<p>hello</p>")
    result = scraper.scrape("http://example.com")
    assert result.find("p").text == "hello"


def test_scrape_raises_on_bad_status(make_scraper):
    scraper = make_scraper(status_code=404)
    with pytest.raises(Exception, match="404"):
        scraper.scrape("http://example.com")

