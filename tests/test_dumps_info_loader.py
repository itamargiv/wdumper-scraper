from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from wdumper_scraper.dumps_info_loader import DumpsInfoLoader
from wdumper_scraper.exceptions import ScraperError
from wdumper_scraper.scraper import CacheDuration, Scraper
from wdumper_scraper.wdumper_client import Dump, DumpSpec, WDumperClient

LAST_ID = 3
RETRY_DELAY = 5.0


@pytest.fixture
def make_loader(
    make_clients: Callable[[], tuple[Scraper, WDumperClient]],
    mocker: MockerFixture,
) -> Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]]:
    def factory(
        last_id: int = LAST_ID,
        fails_on: dict[int, Exception | int] | None = None,
    ) -> tuple[DumpsInfoLoader, MagicMock, MagicMock]:
        """
        fails_on: mapping of dump_id → failure behavior.
          - Exception instance: always raise that specific exception.
          - int: raise a generic ScraperError that many times, then succeed.
        """
        fails_on = fails_on or {}
        call_counts: dict[int, int] = {}

        scraper, wdumper = make_clients()

        mock_recent_page = mocker.MagicMock()
        mock_recent_page.extract_last_id.return_value = last_id
        mock_rdp_class = mocker.patch(
            "wdumper_scraper.dumps_info_loader.RecentDumpsPage",
            return_value=mock_recent_page,
        )

        def get_dump_side_effect(
            dump_id: int, _: CacheDuration
        ) -> tuple[str, Dump]:
            effect = fails_on.get(dump_id)
            if isinstance(effect, Exception):
                raise effect
            elif isinstance(effect, int):
                call_counts[dump_id] = call_counts.get(dump_id, 0) + 1
                if call_counts[dump_id] <= effect:
                    raise ScraperError(f"Transient error on {dump_id}")

            spec: DumpSpec = {
                "languages": None,
                "labels": True,
                "descriptions": True,
                "aliases": True,
                "sitelinks": True,
            }
            dump: Dump = {
                "id": dump_id,
                "title": f"Dump {dump_id}",
                "spec": spec,
            }

            return f"http://example.com/dump/{dump_id}", dump

        mocker.patch.object(
            wdumper, "get_dump", side_effect=get_dump_side_effect
        )
        mock_sleep = mocker.patch("wdumper_scraper.scrape_reporter.time.sleep")

        return DumpsInfoLoader(scraper, wdumper), mock_sleep, mock_rdp_class

    return factory


def test_scrape_attempts_all_ids(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, *_ = make_loader(last_id=LAST_ID)
    result = loader.scrape()
    scraped_ids = {dump["id"] for dump in result.dumps}
    assert scraped_ids == set(range(1, LAST_ID + 1))


def test_scrape_successful_dumps_appear_in_dumps(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, *_ = make_loader(last_id=LAST_ID)
    result = loader.scrape()
    assert len(result.dumps) == LAST_ID
    assert len(result.skipped) == 0


def test_scrape_exception_populates_skipped(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    error = ScraperError("Not found")
    loader, *_ = make_loader(last_id=LAST_ID, fails_on={2: error})
    result = loader.scrape()
    assert len(result.dumps) == LAST_ID - 1
    assert len(result.skipped) == 1
    assert result.skipped[0]["id"] == 2
    assert result.skipped[0]["error"] == str(error)


def test_scrape_skipped_contains_id_and_error_keys(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, *_ = make_loader(last_id=1, fails_on={1: ScraperError("boom")})
    result = loader.scrape()
    assert set(result.skipped[0].keys()) == {"id", "error"}


def test_repeated_scrape_calls_produce_independent_results(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, *_ = make_loader(last_id=LAST_ID)
    result1 = loader.scrape()
    result2 = loader.scrape()
    assert result1 is not result2
    assert result1.dumps is not result2.dumps
    assert result1.skipped is not result2.skipped


def test_scrape_dumps_are_sorted_by_id_descending(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, *_ = make_loader(last_id=LAST_ID)
    result = loader.scrape()
    ids = [dump["id"] for dump in result.dumps]
    assert ids == sorted(ids, reverse=True)


def test_scrape_skipped_are_sorted_by_id_descending(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, *_ = make_loader(
        last_id=LAST_ID,
        fails_on={i: ScraperError("boom") for i in range(1, LAST_ID + 1)},
    )
    result = loader.scrape()
    ids = [entry["id"] for entry in result.skipped]
    assert ids == sorted(ids, reverse=True)


# --- retry ---


def test_scrape_recovers_skipped_ids(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, *_ = make_loader(last_id=LAST_ID, fails_on={2: 1})
    result = loader.scrape(max_retries=1, retry_delay=RETRY_DELAY)
    scraped_ids = {dump["id"] for dump in result.dumps}
    assert scraped_ids == set(range(1, LAST_ID + 1))
    assert result.skipped == []


def test_scrape_exhausted_retries_remain_in_skipped(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, *_ = make_loader(last_id=LAST_ID, fails_on={2: 99})
    result = loader.scrape(max_retries=3, retry_delay=RETRY_DELAY)
    skipped_ids = [entry["id"] for entry in result.skipped]
    assert skipped_ids == [2]
    scraped_ids = {dump["id"] for dump in result.dumps}
    assert 2 not in scraped_ids


def test_scrape_sleep_called_once_per_retry_pass(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    # ID 2 fails on passes 1 and 2, recovers on pass 3 → 2 sleeps
    loader, mock_sleep, _ = make_loader(last_id=LAST_ID, fails_on={2: 2})
    loader.scrape(max_retries=3, retry_delay=RETRY_DELAY)
    assert mock_sleep.call_count == 2
    mock_sleep.assert_called_with(RETRY_DELAY)


def test_scrape_no_sleep_when_no_failures(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, mock_sleep, _ = make_loader(last_id=LAST_ID)
    loader.scrape(retry_delay=RETRY_DELAY)
    mock_sleep.assert_not_called()


def test_scrape_merged_dumps_sorted_by_id_descending(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, *_ = make_loader(last_id=LAST_ID, fails_on={2: 1})
    result = loader.scrape(retry_delay=RETRY_DELAY)
    ids = [dump["id"] for dump in result.dumps]
    assert ids == sorted(ids, reverse=True)


# --- last_id parameter ---


def test_scrape_explicit_last_id_uses_provided_value(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    explicit_last_id = LAST_ID + 2
    loader, *_ = make_loader(last_id=LAST_ID)
    result = loader.scrape(last_id=explicit_last_id)
    scraped_ids = {dump["id"] for dump in result.dumps}
    assert scraped_ids == set(range(1, explicit_last_id + 1))


def test_scrape_explicit_last_id_skips_recent_dumps_page(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, _, mock_rdp_class = make_loader(last_id=LAST_ID)
    loader.scrape(last_id=LAST_ID)
    mock_rdp_class.assert_not_called()


def test_scrape_without_explicit_last_id_calls_recent_dumps_page(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, _, mock_rdp_class = make_loader(last_id=LAST_ID)
    loader.scrape()
    mock_rdp_class.assert_called_once()


def test_scrape_zero_last_id_calls_recent_dumps_page(
    make_loader: Callable[..., tuple[DumpsInfoLoader, MagicMock, MagicMock]],
) -> None:
    loader, _, mock_rdp_class = make_loader(last_id=LAST_ID)
    loader.scrape(last_id=0)
    mock_rdp_class.assert_called_once()
