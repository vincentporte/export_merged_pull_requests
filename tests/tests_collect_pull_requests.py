from unittest.mock import MagicMock, patch

import pytest

from scripts.collect_pull_requests import (
    extract_next_url,
    fetch_pull_requests,
    format_pull_requests,
    get_filename,
)


@patch.dict("scripts.collect_pull_requests.__dict__", {"REPO": "repo", "USERNAME": "username"})
def test_get_filename(monkeypatch):
    start_date = "2025-05-17"
    end_date = "2025-07-16"
    monkeypatch.setenv("USERNAME", "username")
    monkeypatch.setenv("REPO", "repo")
    
    expected_filename = f"data/PRs_repo_{start_date}_{end_date}_username.md"
    assert get_filename(start_date, end_date) == expected_filename

@pytest.mark.parametrize("headers, expected_url", [
    (
        {"Link": '<https://api.github.com/next>; rel="next", <https://api.github.com/last>; rel="last"'},
        "https://api.github.com/next",
    ),
    (
        {"Link": '<https://api.github.com/last>; rel="last"'},
        None,
    ),
    ({}, None),
])
def test_extract_next_url(headers, expected_url):
    assert extract_next_url(headers) == expected_url

@pytest.mark.parametrize("status_code, response_json, expected_items, expected_headers", [
    (200, {"items": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}], {"Link": "<https://test.com>; rel=\"next\""}),
    (404, {}, [], {"Link": ""}),
    (500, {}, [], {"Link": ""}),
])
def test_fetch_pull_requests(status_code, response_json, expected_items, expected_headers):
    url = "https://test.com/"
    headers = {"Authorization": "token test"}
    params = {"q": "test"}

    with patch("requests.get") as mock_get:
        mock_response = MagicMock() 
        mock_response.status_code = status_code
        mock_response.json.return_value = response_json
        mock_response.headers = expected_headers
        mock_get.return_value = mock_response
      
        assert fetch_pull_requests(url, headers, params) == (expected_items, expected_headers)
        mock_get.assert_called_once_with(url, headers=headers, params=params)

@pytest.mark.parametrize("labels", [
    (["bug", "enhancement"], "Labels: bug, enhancement"),
    ([], "No labels"),
])
def test_format_pull_request(labels):
    pr = {
        "number": 123,
        "title": "Test PR",
        "body": "This is a test PR.",
        "closed_at": "2023-10-01T12:00:00Z",
        "labels": [{"name": label} for label in labels[0]],
    }
    
    expected_output = (
        f"## PR #{pr['number']} - {pr['title']}\n\n"
        f"{pr['body']}\n\n"
        f"Merged At: {pr['closed_at']}\n\n"
        f"{labels[1]}\n\n"
    )
    
    assert format_pull_requests(pr) == expected_output

