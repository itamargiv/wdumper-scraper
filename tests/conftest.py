import pytest
from wdumper_scraper import Scraper, WDumperClient


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


@pytest.fixture
def make_client(mocker):
    def factory(status_code=200, json_data=None):
        if json_data is None:
            json_data = {"dump": {"id": 42, "title": "My Dump", "spec": {"labels": True}}}

        mock_response = mocker.MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response

        return WDumperClient(mock_session), mock_session

    return factory


@pytest.fixture
def make_clients(mocker):
    def factory():
        mock_scraper = mocker.MagicMock(spec=Scraper)
        mock_wdumper = mocker.MagicMock(spec=WDumperClient)
        return mock_scraper, mock_wdumper

    return factory
