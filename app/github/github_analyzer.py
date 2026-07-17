from collections import Counter
from datetime import datetime, timezone

from app.github.domain_keywords import DOMAIN_KEYWORDS


def repository_count(repositories):
    """
    Returns total repository count.
    """
    return len(repositories)


def top_languages(language_lists):
    """
    Returns top 5 languages.
    """

    counter = Counter()

    for languages in language_lists:
        if languages:
            counter.update(languages)

    return [
        language
        for language, _
        in counter.most_common(5)
    ]


def documentation_quality(readmes):
    """
    Rates README quality.
    """

    if not readmes:
        return "Poor"

    lengths = [
        len((readme or "").strip())
        for readme in readmes
    ]

    average = sum(lengths) / len(lengths)

    if average >= 700:
        return "Excellent"

    if average >= 300:
        return "Good"

    if average >= 100:
        return "Average"

    return "Poor"


def activity_level(repositories):
    """
    Determines GitHub activity.
    """

    if not repositories:
        return "Inactive"

    dates = [
        datetime.fromisoformat(
            repo["updated_at"].replace("Z", "+00:00")
        )
        for repo in repositories
        if repo.get("updated_at")
    ]

    # Defensive: if every repo is somehow missing updated_at, don't crash
    # on max() over an empty sequence — treat it the same as no data.
    if not dates:
        return "Inactive"

    latest = max(dates)

    now = datetime.now(timezone.utc)

    days = (now - latest).days

    if days <= 30:
        return "Very Active"

    if days <= 90:
        return "Active"

    if days <= 180:
        return "Moderately Active"

    return "Inactive"


def analyze_domains(repo_data):
    """
    Detects project domains.
    """

    detected = set()

    for repo in repo_data:

        name = repo.get("name") or ""
        description = repo.get("description") or ""
        languages = repo.get("languages") or []
        topics = repo.get("topics") or []
        readme = repo.get("readme") or ""

        text = (
            name + " " +
            description + " " +
            " ".join(languages) + " " +
            " ".join(topics) + " " +
            readme
        ).lower()

        for domain, keywords in DOMAIN_KEYWORDS.items():

            if any(keyword.lower() in text for keyword in keywords):
                detected.add(domain)

    return sorted(detected)


def technology_inventory(repo_data):
    """
    Detects technologies.

    NOTE: this currently draws from the same DOMAIN_KEYWORDS dict used by
    analyze_domains() above. If that dict mixes domain terms (e.g.
    "healthcare", "finance") in with actual technology names (e.g.
    "FastAPI", "Docker"), this function will return domain words as if
    they were technologies. Worth confirming domain_keywords.py keeps
    those separate — if it doesn't, this function should read from its
    own TECHNOLOGY_KEYWORDS list instead of reusing DOMAIN_KEYWORDS.
    """

    technologies = set()

    for repo in repo_data:

        name = repo.get("name") or ""
        description = repo.get("description") or ""
        languages = repo.get("languages") or []
        topics = repo.get("topics") or []
        readme = repo.get("readme") or ""

        text = (
            name + " " +
            description + " " +
            " ".join(languages) + " " +
            " ".join(topics) + " " +
            readme
        ).lower()

        for keywords in DOMAIN_KEYWORDS.values():

            for keyword in keywords:

                if keyword.lower() in text:
                    technologies.add(keyword)

    return sorted(technologies)


def profile_strength(
    repositories,
    documentation,
    activity,
    verified_skill_score
):
    """
    Overall GitHub profile quality.

    verified_skill_score should be a 0-100 number, OR None when there was
    nothing to check (e.g. the candidate claimed zero technical skills).
    None is NOT the same as a low score, and must not be punished the same
    way a real 0% consistency result would be -- that was the same mistake
    already caught and fixed in the Confidence Score design, showing up
    here too. When it's None, that criterion is left out of scoring
    entirely and the bands are re-based over 4 points instead of 5.
    """

    score = 0
    max_possible = 5

    if len(repositories) >= 10:
        score += 1

    if documentation in ["Good", "Excellent"]:
        score += 1

    if activity in ["Active", "Very Active"]:
        score += 1

    if verified_skill_score is None:
        # Nothing to check -- exclude this criterion rather than
        # silently scoring it as 0/failed.
        max_possible -= 1
    elif verified_skill_score >= 70:
        score += 1

    total_stars = sum(
        repo.get("stars", 0)
        for repo in repositories
    )

    if total_stars >= 25:
        score += 1

    # Rescale onto the original 0-5 band thresholds below, so a candidate
    # missing one inapplicable criterion is judged on the same scale as
    # everyone else, not capped below them by default.
    normalized_score = round((score / max_possible) * 5) if max_possible else 0

    if normalized_score <= 1:
        return "Weak"

    if normalized_score == 2:
        return "Average"

    if normalized_score == 3:
        return "Good"

    if normalized_score == 4:
        return "Very Good"

    return "Excellent"