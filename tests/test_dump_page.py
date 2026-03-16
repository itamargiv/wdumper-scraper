import pytest
from wdumper_scraper import DumpPage, ScraperError, PageError

DUMP_ID = 42
WITH_H2_HTML = "<h2>My Dump</h2><p>some content</p>"
WITHOUT_H2_HTML = "<p>some content</p>"
WITH_SPEC_HTML = '<h2>Spec</h2><pre>{"key": "value"}</pre>'
WITH_SPEC_HEADING_BUT_NO_PRE_HTML = "<h2>Spec</h2>"
INVALID_JSON_SPEC_HTML = "<h2>Spec</h2><pre>not valid json</pre>"


def test_scrape_called_with_correct_url(make_scraper, mocker):
    scraper = make_scraper(body=WITH_H2_HTML)
    mocker.spy(scraper, "scrape")
    DumpPage(scraper, DUMP_ID)
    scraper.scrape.assert_called_once_with(f"https://wdumps.toolforge.org/dump/{DUMP_ID}", mocker.ANY)


def test_dump_id_property(make_scraper):
    scraper = make_scraper(body=WITH_H2_HTML)
    page = DumpPage(scraper, DUMP_ID)
    assert page.dump_id == DUMP_ID


def test_url_property(make_scraper):
    scraper = make_scraper(body=WITH_H2_HTML)
    page = DumpPage(scraper, DUMP_ID)
    assert page.url == f"https://wdumps.toolforge.org/dump/{DUMP_ID}"


def test_extract_name_returns_h2_text(make_scraper):
    scraper = make_scraper(body=WITH_H2_HTML)
    page = DumpPage(scraper, DUMP_ID)
    assert page.extract_name() == "My Dump"


def test_extract_name_returns_empty_string_when_no_h2(make_scraper):
    scraper = make_scraper(body=WITHOUT_H2_HTML)
    page = DumpPage(scraper, DUMP_ID)
    assert page.extract_name() == ""


def test_init_raises_on_bad_status(make_scraper):
    scraper = make_scraper(status_code=404)
    with pytest.raises(ScraperError):
        DumpPage(scraper, DUMP_ID)


def test_extract_spec_returns_parsed_dict(make_scraper):
    scraper = make_scraper(body=WITH_SPEC_HTML)
    page = DumpPage(scraper, DUMP_ID)
    assert page.extract_spec() == {"key": "value"}


def test_extract_spec_returns_none_when_no_spec_heading(make_scraper):
    scraper = make_scraper(body=WITHOUT_H2_HTML)
    page = DumpPage(scraper, DUMP_ID)
    assert page.extract_spec() is None


def test_extract_spec_returns_none_when_spec_heading_has_no_pre(make_scraper):
    scraper = make_scraper(body=WITH_SPEC_HEADING_BUT_NO_PRE_HTML)
    page = DumpPage(scraper, DUMP_ID)
    assert page.extract_spec() is None


def test_extract_spec_raises_page_error_on_invalid_json(make_scraper):
    scraper = make_scraper(body=INVALID_JSON_SPEC_HTML)
    page = DumpPage(scraper, DUMP_ID)
    with pytest.raises(PageError):
        page.extract_spec()


def test_extract_spec_raises_page_error_on_attribute_error(make_scraper, mocker):
    scraper = make_scraper(body=WITH_SPEC_HTML)
    page = DumpPage(scraper, DUMP_ID)
    mock_soup = mocker.MagicMock()
    mock_soup.find.side_effect = AttributeError("soup broken")
    page._DumpPage__soup = mock_soup
    with pytest.raises(PageError):
        page.extract_spec()


