from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.verification_report import VerificationReport

from app.services.github_service import (
    fetch_repositories,
    fetch_languages,
    fetch_topics,
    fetch_readme
)

from app.github.skill_matcher import verify_github_skills

from app.github.github_analyzer import (
    repository_count,
    top_languages,
    documentation_quality,
    activity_level,
    analyze_domains,
    technology_inventory,
    profile_strength
)
from app.services.confidence_service import calculate_confidence
from app.services.recommendation_service import update_recommendation


def _save_report(db, resume_id, status, score, details):
    """
    Small helper so the create/update-existing branches below don't
    duplicate the same six lines twice.
    """
    existing = (
        db.query(VerificationReport)
        .filter(
            VerificationReport.resume_id == resume_id,
            VerificationReport.verification_type == "github"
        )
        .first()
    )

    if existing:
        existing.status = status
        existing.score = score
        existing.details = details
        db.commit()
        db.refresh(existing)
        report = existing
    else:
        report = VerificationReport(
            resume_id=resume_id,
            verification_type="github",
            status=status,
            score=score,
            details=details
        )
        db.add(report)
        db.commit()
        db.refresh(report)

    return report


def verify_github(
    db: Session,
    resume_id: int,
    github_username: str
):
    """
    Verify candidate GitHub profile and generate recruiter insights.
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
        .filter(
            ParsedResume.resume_id == resume_id
        )
        .first()
    )

    if parsed is None:
        raise Exception("Parsed resume not found.")

    # -------------------------
    # Resume Skills
    # -------------------------

    claimed_skills = []

    if parsed.technical_skills:
        claimed_skills = [
            skill.strip()
            for skill in parsed.technical_skills.split(",")
            if skill.strip()
        ]
    print("=" * 60)
    print("TECHNICAL SKILLS FROM DATABASE")
    print(parsed.technical_skills)
    print("CLAIMED SKILLS")
    print(claimed_skills)
    print("=" * 60)
    # -------------------------
    # Fetch GitHub Repositories
    # -------------------------

    repositories = fetch_repositories(github_username)

    # username doesn't exist / API call failed outright
    if repositories is None:
        report = _save_report(
            db, resume_id,
            status="failed",
            score=0,
            details={"reason": "GitHub profile not found."}
        )
        calculate_confidence(db=db, resume_id=resume_id)
        update_recommendation(db=db, resume_id=resume_id)
        return report

    # valid username, but zero public repositories — genuinely different
    # from a bad username, and shouldn't be silently scored as "verified"
    if len(repositories) == 0:
        report = _save_report(
            db, resume_id,
            status="failed",
            score=0,
            details={"reason": "GitHub profile has no public repositories to verify against."}
        )
        calculate_confidence(db=db, resume_id=resume_id)
        update_recommendation(db=db, resume_id=resume_id)
        return report

    # -------------------------
    # Collect Repository Data
    # -------------------------

    repo_data = []
    language_lists = []
    readmes = []

    for repo in repositories:
        # repo["owner"] is already the username string — fetch_repositories()
        # flattens it before returning. Do not index it again.
        owner = repo["owner"]
        repo_name = repo["name"]

        languages = fetch_languages(owner, repo_name)
        topics = fetch_topics(owner, repo_name)
        readme = fetch_readme(owner, repo_name)

        language_lists.append(languages)
        readmes.append(readme)

        repo_data.append({
            "name": repo["name"],
            "description": repo.get("description", ""),
            "languages": languages,
            "topics": topics,
            "readme": readme,
            "stars": repo.get("stars", 0),
            "forks": repo.get("forks", 0),
            "updated_at": repo.get("updated_at"),
        })

    # -------------------------
    # Skill Verification
    # -------------------------

    result = verify_github_skills(
        claimed_skills,
        [language for lst in language_lists for language in lst],
        [topic for repo in repo_data for topic in repo["topics"]],
        readmes
    )

    verified = result["verified_skills"]
    missing = result["missing_skills"]

    # Per the frozen design: zero claimed technical skills means there was
    # nothing to check, not that verification failed. That's "not
    # computable," never a 0 — a 0 implies evidence was checked and came
    # up empty, which isn't what happened here.
    if len(claimed_skills) == 0:
        score = None
        skill_status = "not_computable"
    else:
        score = round(len(verified) / len(claimed_skills) * 100, 2)
        skill_status = "verified"

    # -------------------------
    # Recruiter Insights
    # -------------------------

    repo_count = repository_count(repositories)
    languages = top_languages(language_lists)
    documentation = documentation_quality(readmes)
    activity = activity_level(repositories)
    domains = analyze_domains(repo_data)
    technologies = technology_inventory(repo_data)
    profile = profile_strength(
        repositories,
        documentation,
        activity,
        score if score is not None else 0
    )

    # -------------------------
    # Save Details
    # -------------------------

    details = {
        "verified_skills": verified,
        "missing_skills": missing,
        "skill_consistency_status": skill_status,
        "repository_count": repo_count,
        "top_languages": languages,
        "documentation_quality": documentation,
        "activity_level": activity,
        "project_domains": domains,
        "technology_inventory": technologies,
        "profile_strength": profile
    }

    report = _save_report(
        db, resume_id,
        status="verified" if skill_status == "verified" else "not_computable",
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