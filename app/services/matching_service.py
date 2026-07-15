from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.job import Job
from app.models.parsed_resume import ParsedResume
from app.models.matching_result import MatchingResult

from app.matching.matcher import calculate_match_score


def build_match_reasons(parsed_resume, job):
    """
    Build explanation for the match.
    """

    resume_skills = []

    if parsed_resume.technical_skills:
        resume_skills = [
            skill.strip()
            for skill in parsed_resume.technical_skills.split(",")
        ]

    job_skills = []

    if job.required_skills:
        job_skills = [
            skill.strip()
            for skill in job.required_skills.split(",")
        ]

    matched = []
    missing = []

    resume_lower = [s.lower() for s in resume_skills]

    for skill in job_skills:

        if skill.lower() in resume_lower:
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "matched_skills": matched,
        "missing_skills": missing
    }


def run_matching(
    db: Session,
    resume_id: int
):
    """
    Runs AI semantic matching and stores the result.
    """

    # -----------------------------
    # Resume
    # -----------------------------
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id)
        .first()
    )

    if resume is None:
        raise Exception("Resume not found.")

    # -----------------------------
    # Job
    # -----------------------------
    job = (
        db.query(Job)
        .filter(Job.id == resume.job_id)
        .first()
    )

    if job is None:
        raise Exception("Job not found.")

    # -----------------------------
    # Parsed Resume
    # -----------------------------
    parsed_resume = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.resume_id == resume.id
        )
        .first()
    )

    if parsed_resume is None:
        raise Exception("Parsed resume not found.")

    # -----------------------------
    # Semantic Match Score
    # -----------------------------
    score = calculate_match_score(
        resume_text=resume.raw_text,
        job_description=job.description_text
    )

    # Convert NumPy float to Python float
    score = round(float(score), 2)

    # -----------------------------
    # Explanation
    # -----------------------------
    reasons = build_match_reasons(
        parsed_resume,
        job
    )

    # -----------------------------
    # Update existing result
    # -----------------------------
    existing = (
        db.query(MatchingResult)
        .filter(
            MatchingResult.resume_id == resume.id
        )
        .first()
    )

    if existing:

        existing.match_score = score
        existing.match_reasons = reasons

        db.commit()
        db.refresh(existing)

        return existing

    # -----------------------------
    # Create new result
    # -----------------------------
    result = MatchingResult(
        resume_id=resume.id,
        job_id=job.id,
        match_score=score,
        match_reasons=reasons,
        confidence_score=None,
        evidence_coverage=None,
        recommendation=None
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return result