import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def _auth_headers():
    """
    Every GitHub API call should carry this. Unauthenticated requests are
    capped at 60/hour total — with 5 repos per candidate and 3 calls per
    repo (languages, topics, readme), a single verification run alone is
    ~16 requests, so the limit gets hit after 2-3 candidates without this.
    Authenticated requests get 5,000/hour instead.
    """
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def fetch_repositories(username: str):
    """
    Fetch latest repositories of a GitHub user.
    Returns simplified repository information.
    """

    url = f"{GITHUB_API}/users/{username}/repos"

    response = requests.get(url, headers=_auth_headers())

    if response.status_code != 200:
        return None

    repos = response.json()

    repos.sort(
        key=lambda x: x["updated_at"],
        reverse=True
    )

    latest = repos[:5]

    repository_list = []

    for repo in latest:

        repository_list.append({

            "name": repo.get("name", ""),

            "owner": repo.get("owner", {}).get("login", ""),

            "description": repo.get("description") or "",

            "updated_at": repo.get("updated_at", ""),

            "stars": repo.get("stargazers_count", 0),

            "forks": repo.get("forks_count", 0),

            "watchers": repo.get("watchers_count", 0),

            "open_issues": repo.get("open_issues_count", 0),

            "default_branch": repo.get("default_branch", "main")

        })

    return repository_list


def fetch_languages(owner: str, repo_name: str):
    """
    Returns programming languages used in a repository.
    """

    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/languages"

    response = requests.get(url, headers=_auth_headers())

    if response.status_code != 200:
        return []

    return list(response.json().keys())


def fetch_topics(owner: str, repo_name: str):
    """
    Returns repository topics.
    """

    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/topics"

    response = requests.get(url, headers=_auth_headers())

    if response.status_code != 200:
        return []

    return response.json().get("names", [])


def fetch_readme(owner: str, repo_name: str):
    """
    Returns decoded README.
    """

    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/readme"

    response = requests.get(url, headers=_auth_headers())

    if response.status_code != 200:
        return ""

    data = response.json()

    content = data.get("content")

    if not content:
        return ""

    try:

        decoded = base64.b64decode(content)

        return decoded.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:

        return ""


def fetch_commit_count(owner: str, repo_name: str):
    """
    Returns approximate commit count.
    """

    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/commits"

    response = requests.get(
        url,
        headers=_auth_headers(),
        params={
            "per_page": 100
        }
    )

    if response.status_code != 200:
        return 0

    return len(response.json())


def fetch_recent_commit(owner: str, repo_name: str):
    """
    Returns latest commit date.
    """

    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/commits"

    response = requests.get(
        url,
        headers=_auth_headers(),
        params={
            "per_page": 1
        }
    )

    if response.status_code != 200:
        return None

    commits = response.json()

    if len(commits) == 0:
        return None

    return commits[0]["commit"]["author"]["date"]