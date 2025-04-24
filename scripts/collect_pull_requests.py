import argparse
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# update with your own in `.env` file
TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_ORGANIZATION_OR_USER")
REPO = os.getenv("REPOSITORY_NAME")
BASE_URL = "https://api.github.com/search/issues"
HEADERS = {"Authorization": f"token {TOKEN}"}

def get_filename(start_date, end_date, username):
    filename = f"data/PRs_{REPO}_{start_date}_{end_date}"
    if username:
        filename += f"_{username}"
    return f"{filename}.md"

def extract_next_url(headers):
    links = headers.get("Link", "")
    match = re.search(r'<(https:[^>]+)>; rel="next"', links)
    return match.group(1) if match else None

def fetch_pull_requests(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("items", []), response.headers
    print(f"Error: {response.status_code}, {response.text}")
    return [], response.headers

def format_pull_request(pull_request):
    labels = [label['name'] for label in pull_request.get('labels', [])]
    labels_text = f"Labels: {', '.join(labels)}" if labels else "No labels"
    return (
        f"## PR #{pull_request['number']} - {pull_request['title']}\n\n"
        f"{pull_request['body']}\n\n"
        f"Merged At: {pull_request['closed_at']}\n\n"
        f"{labels_text}\n\n"
    )

def save_to_file(filename, content):
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")

def main():
    if not TOKEN or not USERNAME or not OWNER or not REPO:
        raise ValueError("Please set GITHUB_TOKEN, GITHUB_USERNAME, GITHUB_ORGANIZATION_OR_USER, "
                         "and REPOSITORY_NAME in your environment variables.")

    parser = argparse.ArgumentParser(description="Fetch merged pull requests from a GitHub repository.")
    parser.add_argument("--start-date", required=True, help="Start date for PRs (YYYY-MM-DD).")
    parser.add_argument("--end-date", required=True, help="End date for PRs (YYYY-MM-DD).")
    parser.add_argument(
        "--username",
        help="GitHub username to filter PRs by assignee. If not provided, fetches PRs for all users.",
    )
    args = parser.parse_args()

    query = (
        f"repo:{OWNER}/{REPO} is:pr is:merged "
        f"merged:{args.start_date}..{args.end_date} sort:updated-desc"
    )
    if args.username:
        query += f" assignee:{args.username}"
        print(f"Fetching PRs for user: {args.username}")
    else:
        print("Fetching PRs for all users.")

    params = {"q": query, "per_page": 100}
    output_filename = get_filename(args.start_date, args.end_date, args.username)
    url = BASE_URL

    formatted_pull_requests = []

    while url:
        pull_requests, response_headers = fetch_pull_requests(url, HEADERS, params)
        if pull_requests:
            print(f"Fetched {len(pull_requests)} pull requests.")
            formatted_pull_requests.extend(format_pull_request(pr) for pr in pull_requests)
        url = extract_next_url(response_headers)

    if formatted_pull_requests:
        save_to_file(output_filename, "".join(formatted_pull_requests))
        print(f"Saved to {output_filename}")
    else:
        print("No pull requests found.")

if __name__ == "__main__":
    main()
