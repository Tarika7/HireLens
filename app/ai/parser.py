import re

from app.ai.skills import (
    TECHNICAL_SKILLS,
    SOFT_SKILLS,
)

EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

PHONE_REGEX = r"(?:\+91[- ]?)?[6-9]\d{9}"


def extract_section(text: str, section_names):
    """
    Extract text belonging to a section until the next section heading.
    """

    lines = text.splitlines()

    collected = []

    capture = False

    headings = {
        "education",
        "academic qualification",
        "experience",
        "work experience",
        "employment",
        "projects",
        "academic projects",
        "skills",
        "technical skills",
        "certifications",
        "certificates",
        "summary",
        "objective",
    }

    for line in lines:

        stripped = line.strip()

        if stripped.lower() in section_names:
            capture = True
            continue

        if capture:

            if stripped.lower() in headings:
                break

            if stripped:
                collected.append(stripped)

    return collected


def parse_resume(text: str):

    data = {}

    # ---------------------------------
    # Email
    # ---------------------------------

    emails = re.findall(
        EMAIL_REGEX,
        text
    )

    data["candidate_email"] = emails[0] if emails else None

    # ---------------------------------
    # Phone
    # ---------------------------------

    phones = re.findall(
        PHONE_REGEX,
        text
    )

    data["candidate_phone"] = phones[0] if phones else None

    # ---------------------------------
    # Candidate Name
    # ---------------------------------

    candidate_name = None

    for line in text.splitlines():

        line = line.strip()

        if len(line) > 3:

            candidate_name = line

            break

    data["candidate_name"] = candidate_name

    # ---------------------------------
    # Skills
    # ---------------------------------

    lower_text = text.lower()

    technical = []

    soft = []

    for skill in TECHNICAL_SKILLS:

        if skill.lower() in lower_text:
            technical.append(skill)

    for skill in SOFT_SKILLS:

        if skill.lower() in lower_text:
            soft.append(skill)

    data["technical_skills"] = sorted(set(technical))

    data["soft_skills"] = sorted(set(soft))

    # ---------------------------------
    # Education
    # ---------------------------------

    data["education"] = extract_section(
        text,
        {"education", "academic qualification"}
    )

    # ---------------------------------
    # Experience
    # ---------------------------------

    data["experience_text"] = extract_section(
        text,
        {"experience", "work experience", "employment"}
    )

    # ---------------------------------
    # Projects
    # ---------------------------------

    data["projects"] = extract_section(
        text,
        {"projects", "academic projects"}
    )

    # ---------------------------------
    # Certifications
    # ---------------------------------

    data["certifications_claimed"] = extract_section(
        text,
        {"certifications", "certificates"}
    )

    return data