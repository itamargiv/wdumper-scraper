import pytest
from RecentDumpsPage import RecentDumpsPage

SINGLE_ROW_HTML = '<table><tr><td><a href="/dump/42">Dump 42</a></td></tr></table>'
MULTI_ROW_HTML = (
    '<table>'
    '<tr><td><a href="/dump/42">Dump 42</a></td></tr>'
    '<tr><td><a href="/dump/99">Dump 99</a></td></tr>'
    '</table>'
)
EMPTY_TABLE_HTML = '<table></table>'
NO_HREF_HTML = '<table><tr><td><a>No href</a></td></tr></table>'
NON_INTEGER_ID_HTML = '<table><tr><td><a href="/dump/abc">Dump abc</a></td></tr></table>'


def test_scrape_called_with_correct_url(make_scraper, mocker):
    scraper = make_scraper(body=SINGLE_ROW_HTML)
    mocker.spy(scraper, "scrape")
    RecentDumpsPage(scraper)
    scraper.scrape.assert_called_once_with("https://wdumps.toolforge.org/dumps")


def test_extract_last_id_returns_correct_id(make_scraper):
    scraper = make_scraper(body=SINGLE_ROW_HTML)
    page = RecentDumpsPage(scraper)
    assert page.extract_last_id() == 42


def test_extract_last_id_returns_first_row_id(make_scraper):
    scraper = make_scraper(body=MULTI_ROW_HTML)
    page = RecentDumpsPage(scraper)
    assert page.extract_last_id() == 42


def test_extract_last_id_raises_on_missing_link(make_scraper):
    scraper = make_scraper(body=EMPTY_TABLE_HTML)
    page = RecentDumpsPage(scraper)
    with pytest.raises(TypeError):
        page.extract_last_id()


def test_extract_last_id_raises_on_missing_href(make_scraper):
    scraper = make_scraper(body=NO_HREF_HTML)
    page = RecentDumpsPage(scraper)
    with pytest.raises(KeyError):
        page.extract_last_id()


def test_extract_last_id_raises_on_non_integer_id(make_scraper):
    scraper = make_scraper(body=NON_INTEGER_ID_HTML)
    page = RecentDumpsPage(scraper)
    with pytest.raises(ValueError):
        page.extract_last_id()


def test_init_raises_on_bad_status(make_scraper):
    scraper = make_scraper(status_code=404)
    with pytest.raises(Exception, match="404"):
        RecentDumpsPage(scraper)


