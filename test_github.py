from app.services.github_service import (
    fetch_repositories,
    fetch_languages,
    fetch_topics,
    fetch_readme
)

repos = fetch_repositories("torvalds")

for repo in repos:

    owner = repo["owner"]["login"]
    name = repo["name"]

    print("=" * 60)
    print("Repository:", name)

    languages = fetch_languages(owner, name)
    print("Languages:", languages)

    topics = fetch_topics(owner, name)
    print("Topics:", topics)

    readme = fetch_readme(owner, name)

    print("\nREADME Preview:\n")

    print(readme[:500])