from unittest.mock import MagicMock, patch

import pytest

from scripts.collect_pull_requests import (
    extract_next_url,
    fetch_pull_requests,
    format_pull_request,
    get_filename,
)


def test_get_filename(monkeypatch):
    assert get_filename("orga/repo", "2025-05-17", "2025-07-16") == "data/PRs_repo_2025-05-17_2025-07-16.md"
    assert get_filename("orga/repo", "2025-05-17", "2025-07-16", "username") == "data/PRs_repo_2025-05-17_2025-07-16_username.md"

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
    
    assert format_pull_request(pr) == expected_output

