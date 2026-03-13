import pytest
from Scraper import Scraper


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

