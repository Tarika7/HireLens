from sqlalchemy.orm import Session

from app.models.verification_report import VerificationReport
from app.models.matching_result import MatchingResult


# --------------------------------------
# Source Weights
# --------------------------------------

SOURCE_WEIGHTS = {
    "github": 50,
    "linkedin": 30,
    "certificate": 20
}


def calculate_confidence(
    db: Session,
    resume_id: int
):
    """
    Calculates confidence score using all
    verification reports.
    """

    reports = (
        db.query(VerificationReport)
        .filter(
            VerificationReport.resume_id == resume_id
        )
        .all()
    )

    matching_result = (
        db.query(MatchingResult)
        .filter(
            MatchingResult.resume_id == resume_id
        )
        .first()
    )

    if matching_result is None:
        raise Exception(
            "Matching result not found."
        )

    applicable_weight = 0

    weighted_sum = 0

    github_present = False

    confidence_reasons = {}

    for report in reports:

        verification_type = report.verification_type

        if verification_type not in SOURCE_WEIGHTS:
            continue

        weight = SOURCE_WEIGHTS[
            verification_type
        ]

        if verification_type == "github":
            github_present = True

        # -----------------------------
        # Submitted source
        # -----------------------------

        if report.status in [
            "verified",
            "failed"
        ]:

            applicable_weight += weight

            if report.status == "verified":

                weighted_sum += (
                    report.score * weight
                )

                confidence_reasons[
                    verification_type
                ] = report.score

            else:

                confidence_reasons[
                    verification_type
                ] = "Failed"

        else:

            confidence_reasons[
                verification_type
            ] = "Not Submitted"

    # -----------------------------
    # Evidence Coverage
    # -----------------------------

    evidence_coverage = round(
        applicable_weight,
        2
    )

    # -----------------------------
    # Guard Rule
    # -----------------------------

    if (
        applicable_weight < 40
        or
        github_present is False
    ):

        matching_result.confidence_score = None

        matching_result.evidence_coverage = (
            evidence_coverage
        )

        matching_result.confidence_reasons = (
            confidence_reasons
        )

        db.commit()

        db.refresh(matching_result)

        return matching_result

    # -----------------------------
    # Confidence Score
    # -----------------------------

    confidence_score = round(
        weighted_sum / applicable_weight,
        2
    )

    matching_result.confidence_score = (
        confidence_score
    )

    matching_result.evidence_coverage = (
        evidence_coverage
    )

    matching_result.confidence_reasons = (
        confidence_reasons
    )

    db.commit()

    db.refresh(matching_result)

    return matching_result