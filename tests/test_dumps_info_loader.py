import pytest
from wdumper_scraper import DumpsInfoLoader

LAST_ID = 3

@pytest.fixture
def make_loader(make_scraper, make_page, mocker):
    def factory(last_id=LAST_ID, side_effects=None):
        scraper = make_scraper()

        mock_recent_page = mocker.MagicMock()
        mock_recent_page.extract_last_id.return_value = last_id
        mocker.patch(
            "wdumper_scraper.dumps_info_loader.RecentDumpsPage",
            return_value=mock_recent_page
        )

        def make_dump_info_page(scraper, dump_id, cache_duration):
            if side_effects and dump_id in side_effects:
                raise side_effects[dump_id]
            return make_page(
                dump_id=dump_id,
                name=f"Dump {dump_id}",
                url=f"http://example.com/dump/{dump_id}",
            )

        mocker.patch(
            "wdumper_scraper.dumps_info_loader.DumpInfoPage",
            side_effect=make_dump_info_page
        )

        return DumpsInfoLoader(scraper)

    return factory


def test_scrape_attempts_all_ids(make_loader):
    loader = make_loader(last_id=LAST_ID)
    result = loader.scrape()
    scraped_ids = {dump["id"] for dump in result.dumps}
    assert scraped_ids == set(range(1, LAST_ID + 1))


def test_scrape_successful_dumps_appear_in_dumps(make_loader):
    loader = make_loader(last_id=LAST_ID)
    result = loader.scrape()
    assert len(result.dumps) == LAST_ID
    assert len(result.skipped) == 0


def test_scrape_exception_populates_skipped(make_loader):
    error = Exception("Not found")
    loader = make_loader(last_id=LAST_ID, side_effects={2: error})
    result = loader.scrape()
    assert len(result.dumps) == LAST_ID - 1
    assert len(result.skipped) == 1
    assert result.skipped[0]["id"] == 2
    assert result.skipped[0]["error"] == str(error)


def test_scrape_skipped_contains_id_and_error_keys(make_loader):
    loader = make_loader(last_id=1, side_effects={1: Exception("boom")})
    result = loader.scrape()
    assert set(result.skipped[0].keys()) == {"id", "error"}


def test_repeated_scrape_calls_produce_independent_results(make_loader):
    loader = make_loader(last_id=LAST_ID)
    result1 = loader.scrape()
    result2 = loader.scrape()
    assert result1 is not result2
    assert result1.dumps is not result2.dumps
    assert result1.skipped is not result2.skipped


def test_scrape_dumps_are_sorted_by_id_descending(make_loader):
    loader = make_loader(last_id=LAST_ID)
    result = loader.scrape()
    ids = [dump["id"] for dump in result.dumps]
    assert ids == sorted(ids, reverse=True)


def test_scrape_skipped_are_sorted_by_id_descending(make_loader):
    loader = make_loader(last_id=LAST_ID, side_effects={i: Exception("boom") for i in range(1, LAST_ID + 1)})
    result = loader.scrape()
    ids = [entry["id"] for entry in result.skipped]
    assert ids == sorted(ids, reverse=True)


