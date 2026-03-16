import json

import pytest
from requests.exceptions import RequestException

from wdumper_scraper import CacheDuration, ClientError

DUMP_ID = 42
BASE_URL = "https://wdumps.toolforge.org"
DUMP_URL = f"{BASE_URL}/dump/{DUMP_ID}"
DEFAULT_SPEC = {"labels": True}
DEFAULT_DUMP = {"id": DUMP_ID, "title": "My Dump", "spec": DEFAULT_SPEC}
DEFAULT_JSON = {"dump": DEFAULT_DUMP}


def test_get_dump_calls_correct_url(make_client):
    client, mock_session = make_client()
    client.get_dump(DUMP_ID)
    args, _ = mock_session.get.call_args
    assert args[0] == DUMP_URL


def test_get_dump_passes_accept_json_header(make_client):
    client, mock_session = make_client()
    client.get_dump(DUMP_ID)
    _, kwargs = mock_session.get.call_args
    assert kwargs["headers"] == {"Accept": "application/json"}


def test_get_dump_forwards_cache_duration(make_client):
    client, mock_session = make_client()
    client.get_dump(DUMP_ID, CacheDuration.SHORT)
    _, kwargs = mock_session.get.call_args
    assert kwargs["expire_after"] == CacheDuration.SHORT.value


def test_get_dump_returns_url_and_dump(make_client):
    client, _ = make_client(json_data=DEFAULT_JSON)
    url, dump = client.get_dump(DUMP_ID)
    assert url == DUMP_URL
    assert dump == DEFAULT_DUMP


def test_get_dump_parses_string_spec(make_client):
    spec = {"labels": True}
    json_data = {"dump": {"id": DUMP_ID, "title": "My Dump", "spec": json.dumps(spec)}}
    client, _ = make_client(json_data=json_data)
    _, dump = client.get_dump(DUMP_ID)
    assert dump["spec"] == spec


def test_get_dump_leaves_dict_spec_unchanged(make_client):
    spec = {"labels": True}
    json_data = {"dump": {"id": DUMP_ID, "title": "My Dump", "spec": spec}}
    client, _ = make_client(json_data=json_data)
    _, dump = client.get_dump(DUMP_ID)
    assert dump["spec"] == spec


def test_get_dump_raises_client_error_on_request_exception(make_client):
    client, mock_session = make_client()
    mock_session.get.side_effect = RequestException("connection refused")
    with pytest.raises(ClientError, match="connection refused"):
        client.get_dump(DUMP_ID)


def test_get_dump_raises_client_error_on_bad_status(make_client):
    client, _ = make_client(status_code=404)
    with pytest.raises(ClientError, match="404"):
        client.get_dump(DUMP_ID)


def test_get_dump_raises_client_error_on_invalid_json_response(make_client):
    client, mock_session = make_client()
    mock_session.get.return_value.json.side_effect = json.decoder.JSONDecodeError("err", "", 0)
    with pytest.raises(ClientError):
        client.get_dump(DUMP_ID)


def test_get_dump_raises_client_error_on_invalid_spec_json(make_client):
    json_data = {"dump": {"id": DUMP_ID, "title": "My Dump", "spec": "not valid json"}}
    client, _ = make_client(json_data=json_data)
    with pytest.raises(ClientError):
        client.get_dump(DUMP_ID)

