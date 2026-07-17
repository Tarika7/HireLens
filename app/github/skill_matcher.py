import re


def verify_github_skills(
    claimed_skills: list[str],
    languages: list[str],
    topics: list[str],
    readmes: list[str]
):
    """
    Verify claimed technical skills using
    GitHub languages, topics and README text.
    """

    verified = []

    missing = []

    github_text = " ".join(
        languages +
        topics +
        readmes
    ).lower()

    github_text = re.sub(
        r"[^a-zA-Z0-9+#.]",
        " ",
        github_text
    )

    for skill in claimed_skills:

        if skill.lower() in github_text:

            verified.append(skill)

        else:

            missing.append(skill)

    return {
        "verified_skills": verified,
        "missing_skills": missing
    }