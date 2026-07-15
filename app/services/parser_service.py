from sqlalchemy.orm import Session

from app.models.parsed_resume import ParsedResume


def save_parsed_resume(
    db: Session,
    resume,
    parsed_data: dict
):
    """
    Save parsed resume information into the database.
    """

    parsed_resume = ParsedResume(

        resume_id=resume.id,

        candidate_name=parsed_data.get("candidate_name"),

        candidate_email=parsed_data.get("candidate_email"),

        candidate_phone=parsed_data.get("candidate_phone"),

        technical_skills=",".join(
            parsed_data.get("technical_skills", [])
        ),

        soft_skills=",".join(
            parsed_data.get("soft_skills", [])
        ),

        education="\n".join(
            parsed_data.get("education", [])
        ),

        experience_text="\n".join(
            parsed_data.get("experience_text", [])
        ),

        projects="\n".join(
            parsed_data.get("projects", [])
        ),

        certifications_claimed="\n".join(
            parsed_data.get("certifications_claimed", [])
        )

    )

    db.add(parsed_resume)

    db.commit()

    db.refresh(parsed_resume)

    return parsed_resume