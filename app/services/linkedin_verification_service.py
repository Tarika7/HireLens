import re

from sqlalchemy.orm import Session

from app.models.parsed_resume import ParsedResume
from app.models.resume import Resume
from app.models.verification_report import VerificationReport
from app.services.confidence_service import calculate_confidence
from app.services.recommendation_service import update_recommendation


def _save_report(db, resume_id, status, score, details):
    existing = (
        db.query(VerificationReport)
        .filter(
            VerificationReport.resume_id == resume_id,
            VerificationReport.verification_type == "linkedin"
        )
        .first()
    )

    if existing:
        existing.status = status
        existing.score = score
        existing.details = details
        db.commit()
        db.refresh(existing)
        return existing

    report = VerificationReport(
        resume_id=resume_id,
        verification_type="linkedin",
        status=status,
        score=score,
        details=details
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def _normalize_name(name: str | None) -> str:
    if not name:
        return ""

    normalized = " ".join(name.split())
    return normalized.strip().lower()


def _normalize_technical_skills(raw_skills: str | None) -> list[str]:
    if not raw_skills:
        return []

    return [
        skill.strip()
        for skill in raw_skills.split(",")
        if skill.strip()
    ]


def _flatten_profile_entries(raw_entries: list[object] | None) -> list[str]:
    if not raw_entries:
        return []

    entries = []

    for entry in raw_entries:
        if isinstance(entry, str):
            normalized = entry.strip()
        elif isinstance(entry, dict):
            normalized = " ".join(
                str(value).strip()
                for value in entry.values()
                if value is not None
            ).strip()
        else:
            normalized = str(entry).strip()

        if normalized:
            entries.append(normalized)

    return entries


def _split_text_entries(text: str | None) -> list[str]:
    if not text:
        return []

    parts = re.split(r"[\n\r;]+", text)
    return [part.strip() for part in parts if part.strip()]


def _matches_any_entry(entry: str, candidates: list[str]) -> bool:
    lowered_entry = entry.lower()

    for candidate in candidates:
        lowered_candidate = candidate.lower()

        if lowered_entry in lowered_candidate:
            return True

        if lowered_candidate in lowered_entry:
            return True

    return False


def _profile_strength(overall_score: float | None) -> str:
    if overall_score is None:
        return "Weak"

    if overall_score >= 90:
        return "Excellent"

    if overall_score >= 75:
        return "Strong"

    if overall_score >= 60:
        return "Average"

    return "Weak"


def verify_linkedin(
    db: Session,
    resume_id: int,
    linkedin_data: dict
):
    """
    Verify candidate LinkedIn profile data against parsed resume fields.
    """

    # -------------------------
    # Resume
    # -------------------------

    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id)
        .first()
    )

    if resume is None:
        raise Exception("Resume not found.")

    # -------------------------
    # Parsed Resume
    # -------------------------

    parsed = (
        db.query(ParsedResume)
        .filter(ParsedResume.resume_id == resume_id)
        .first()
    )

    if parsed is None:
        raise Exception("Parsed resume not found.")

    candidate_name = parsed.candidate_name
    technical_skills = parsed.technical_skills
    education_text = parsed.education
    experience_text = parsed.experience_text
    projects = parsed.projects

    # -------------------------
    # LinkedIn Profile
    # -------------------------

    profile_url = linkedin_data.get("profile_url")
    full_name = linkedin_data.get("full_name") or ""
    headline = linkedin_data.get("headline")
    skills = linkedin_data.get("skills") or []
    experience = linkedin_data.get("experience") or []
    education = linkedin_data.get("education") or []

    linkedin_skill_names = [
        skill.strip()
        for skill in skills
        if isinstance(skill, str) and skill.strip()
    ]

    has_profile_url = bool(
        isinstance(profile_url, str)
        and profile_url.strip()
    )

    # -------------------------
    # Name Verification
    # -------------------------

    name_verified = (
        _normalize_name(candidate_name)
        == _normalize_name(full_name)
    )

    name_status = "verified" if name_verified else "failed"
    name_score = 100 if name_verified else 0

    # -------------------------
    # Technical Skills Verification
    # -------------------------

    claimed_skills = _normalize_technical_skills(technical_skills)
    verified_skills = []
    missing_skills = []

    if len(claimed_skills) > 0:
        linkedin_lower_skills = [skill.lower() for skill in linkedin_skill_names]

        for claimed_skill in claimed_skills:
            if claimed_skill.lower() in linkedin_lower_skills:
                verified_skills.append(claimed_skill)
            else:
                missing_skills.append(claimed_skill)

        skill_score = round(
            len(verified_skills) / len(claimed_skills) * 100,
            2
        )
    else:
        skill_score = None

    # -------------------------
    # Education Verification
    # -------------------------

    resume_education_entries = _split_text_entries(education_text)
    linkedin_education_entries = _flatten_profile_entries(education)
    verified_education = []
    missing_education = []

    for entry in resume_education_entries:
        if _matches_any_entry(entry, linkedin_education_entries):
            verified_education.append(entry)
        else:
            missing_education.append(entry)

    education_score = None

    if len(resume_education_entries) > 0:
        education_score = round(
            len(verified_education) / len(resume_education_entries) * 100,
            2
        )

    # -------------------------
    # Experience Verification
    # -------------------------

    resume_experience_entries = _split_text_entries(experience_text)
    linkedin_experience_entries = _flatten_profile_entries(experience)
    verified_experience = []
    missing_experience = []

    for entry in resume_experience_entries:
        if _matches_any_entry(entry, linkedin_experience_entries):
            verified_experience.append(entry)
        else:
            missing_experience.append(entry)

    experience_score = None

    if len(resume_experience_entries) > 0:
        experience_score = round(
            len(verified_experience) / len(resume_experience_entries) * 100,
            2
        )

    # -------------------------
    # Overall Verification Score
    # -------------------------

    overall_components = [
        name_score,
        skill_score,
        education_score,
        experience_score
    ]

    overall_score = None

    computable_components = [
        value for value in overall_components
        if value is not None
    ]

    if len(computable_components) > 0:
        overall_score = round(
            sum(computable_components) / len(computable_components),
            2
        )

    # -------------------------
    # Status
    # -------------------------

    if not has_profile_url:
        status = "failed"
        score = 0
    elif len(claimed_skills) == 0:
        status = "not_computable"
        score = None
    else:
        status = "verified"
        score = overall_score

    profile_strength = _profile_strength(overall_score)

    details = {
        "name_status": name_status,
        "name_score": name_score,
        "verified_skills": verified_skills,
        "missing_skills": missing_skills,
        "skill_score": skill_score,
        "verified_education": verified_education,
        "missing_education": missing_education,
        "education_score": education_score,
        "verified_experience": verified_experience,
        "missing_experience": missing_experience,
        "experience_score": experience_score,
        "profile_strength": profile_strength,
        "headline": headline,
        "linkedin_skill_count": len(linkedin_skill_names)
    }

    report = _save_report(
        db,
        resume_id,
        status=status,
        score=score,
        details=details
    )

    calculate_confidence(
        db=db,
        resume_id=resume_id
    )

    update_recommendation(
        db=db,
        resume_id=resume_id
    )

    return report
