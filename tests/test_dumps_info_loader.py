import pytest
from wdumper_scraper import DumpsInfoLoader, ScraperError

LAST_ID = 3
RETRY_DELAY = 5.0


@pytest.fixture
def make_loader(make_scraper, make_page, mocker):
    def factory(last_id=LAST_ID, fails_on: dict[int, Exception | int] = None):
        """
        fails_on: mapping of dump_id → failure behaviour.
          - Exception instance: always raise that specific exception.
          - int: raise a generic ScraperError that many times, then succeed.
        """
        fails_on = fails_on or {}
        call_counts = {}

        scraper = make_scraper()

        mock_recent_page = mocker.MagicMock()
        mock_recent_page.extract_last_id.return_value = last_id
        mocker.patch(
            "wdumper_scraper.dumps_info_loader.RecentDumpsPage",
            return_value=mock_recent_page,
        )

        def make_dump_page(scraper, dump_id, cache_duration):
            effect = fails_on.get(dump_id)
            if isinstance(effect, Exception):
                raise effect
            elif isinstance(effect, int):
                call_counts[dump_id] = call_counts.get(dump_id, 0) + 1
                if call_counts[dump_id] <= effect:
                    raise ScraperError(f"Transient error on {dump_id}")
            return make_page(
                dump_id=dump_id,
                name=f"Dump {dump_id}",
                url=f"http://example.com/dump/{dump_id}",
            )

        mocker.patch(
            "wdumper_scraper.dumps_info_loader.DumpPage",
            side_effect=make_dump_page,
        )
        mock_sleep = mocker.patch("wdumper_scraper.dumps_info_loader.time.sleep")

        return DumpsInfoLoader(scraper), mock_sleep

    return factory


def test_scrape_attempts_all_ids(make_loader):
    loader, _ = make_loader(last_id=LAST_ID)
    result = loader.scrape()
    scraped_ids = {dump["id"] for dump in result.dumps}
    assert scraped_ids == set(range(1, LAST_ID + 1))


def test_scrape_successful_dumps_appear_in_dumps(make_loader):
    loader, _ = make_loader(last_id=LAST_ID)
    result = loader.scrape()
    assert len(result.dumps) == LAST_ID
    assert len(result.skipped) == 0


def test_scrape_exception_populates_skipped(make_loader):
    error = ScraperError("Not found")
    loader, _ = make_loader(last_id=LAST_ID, fails_on={2: error})
    result = loader.scrape()
    assert len(result.dumps) == LAST_ID - 1
    assert len(result.skipped) == 1
    assert result.skipped[0]["id"] == 2
    assert result.skipped[0]["error"] == str(error)


def test_scrape_skipped_contains_id_and_error_keys(make_loader):
    loader, _ = make_loader(last_id=1, fails_on={1: ScraperError("boom")})
    result = loader.scrape()
    assert set(result.skipped[0].keys()) == {"id", "error"}


def test_repeated_scrape_calls_produce_independent_results(make_loader):
    loader, _ = make_loader(last_id=LAST_ID)
    result1 = loader.scrape()
    result2 = loader.scrape()
    assert result1 is not result2
    assert result1.dumps is not result2.dumps
    assert result1.skipped is not result2.skipped


def test_scrape_dumps_are_sorted_by_id_descending(make_loader):
    loader, _ = make_loader(last_id=LAST_ID)
    result = loader.scrape()
    ids = [dump["id"] for dump in result.dumps]
    assert ids == sorted(ids, reverse=True)


def test_scrape_skipped_are_sorted_by_id_descending(make_loader):
    loader, _ = make_loader(last_id=LAST_ID, fails_on={i: ScraperError("boom") for i in range(1, LAST_ID + 1)})
    result = loader.scrape()
    ids = [entry["id"] for entry in result.skipped]
    assert ids == sorted(ids, reverse=True)


# --- retry ---

def test_scrape_recovers_skipped_ids(make_loader):
    loader, _ = make_loader(last_id=LAST_ID, fails_on={2: 1})
    result = loader.scrape(max_retries=1, retry_delay=RETRY_DELAY)
    scraped_ids = {dump["id"] for dump in result.dumps}
    assert scraped_ids == set(range(1, LAST_ID + 1))
    assert result.skipped == []


def test_scrape_exhausted_retries_remain_in_skipped(make_loader):
    loader, _ = make_loader(last_id=LAST_ID, fails_on={2: 99})
    result = loader.scrape(max_retries=3, retry_delay=RETRY_DELAY)
    skipped_ids = [entry["id"] for entry in result.skipped]
    assert skipped_ids == [2]
    scraped_ids = {dump["id"] for dump in result.dumps}
    assert 2 not in scraped_ids


def test_scrape_sleep_called_once_per_retry_pass(make_loader):
    # ID 2 fails on passes 1 and 2, recovers on pass 3 → 2 sleeps
    loader, mock_sleep = make_loader(last_id=LAST_ID, fails_on={2: 2})
    loader.scrape(max_retries=3, retry_delay=RETRY_DELAY)
    assert mock_sleep.call_count == 2
    mock_sleep.assert_called_with(RETRY_DELAY)


def test_scrape_no_sleep_when_no_failures(make_loader):
    loader, mock_sleep = make_loader(last_id=LAST_ID)
    loader.scrape(retry_delay=RETRY_DELAY)
    mock_sleep.assert_not_called()


def test_scrape_merged_dumps_sorted_by_id_descending(make_loader):
    loader, _ = make_loader(last_id=LAST_ID, fails_on={2: 1})
    result = loader.scrape(retry_delay=RETRY_DELAY)
    ids = [dump["id"] for dump in result.dumps]
    assert ids == sorted(ids, reverse=True)
