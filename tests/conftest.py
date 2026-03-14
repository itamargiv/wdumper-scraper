import pytest
from wdumper_scraper import Scraper


@pytest.fixture
def make_page(mocker):
    def factory(dump_id=42, name="My Dump", url="https://wdumps.toolforge.org/dump/42", spec=None):
        page = mocker.MagicMock()
        page.dump_id = dump_id
        page.url = url
        page.extract_name.return_value = name
        page.extract_spec.return_value = spec
        return page

    return factory


@pytest.fixture
def make_scraper(mocker):
    def factory(status_code=200, body="<p>hello</p>"):
        mock_response = mocker.MagicMock()
        mock_response.status_code = status_code
        mock_response.text = body

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response

        return Scraper(mock_session)

    return factory

