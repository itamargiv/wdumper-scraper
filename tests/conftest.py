from collections.abc import Callable
from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from wdumper_scraper import Scraper, WDumperClient


@pytest.fixture
def make_scraper(mocker: MockerFixture) -> Callable[..., Scraper]:
    def factory(status_code: int = 200, body: str = "<p>hello</p>") -> Scraper:
        mock_response = mocker.MagicMock()
        mock_response.status_code = status_code
        mock_response.text = body

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response

        return Scraper(mock_session)

    return factory


@pytest.fixture
def make_client(
    mocker: MockerFixture,
) -> Callable[..., tuple[WDumperClient, MagicMock]]:
    def factory(
        status_code: int = 200, json_data: dict[str, Any] | None = None
    ) -> tuple[WDumperClient, MagicMock]:
        if json_data is None:
            json_data = {
                "dump": {"id": 42, "title": "My Dump", "spec": {"labels": True}}
            }

        mock_response = mocker.MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_response

        return WDumperClient(mock_session), mock_session

    return factory


@pytest.fixture
def make_clients(
    mocker: MockerFixture,
) -> Callable[[], tuple[Scraper, WDumperClient]]:
    def factory() -> tuple[Scraper, WDumperClient]:
        mock_scraper = cast(Scraper, mocker.MagicMock(spec=Scraper))
        mock_wdumper = cast(WDumperClient, mocker.MagicMock(spec=WDumperClient))
        return mock_scraper, mock_wdumper

    return factory
