from sqlalchemy.orm import Session

from app.models.matching_result import MatchingResult


def _match_band(match_score: float) -> str:
    """
    Per SRS §7.4: High >=80, Medium 50-79, Low <50.
    """
    if match_score >= 80:
        return "High"
    if match_score >= 50:
        return "Medium"
    return "Low"


def _confidence_band(confidence_score: float | None) -> str:
    """
    Per the agreed threshold revision: High >=70, Medium 40-69, Low <40.
    None means Evidence Coverage was insufficient to compute a score at
    all (see §7.3's guard rule) -- this is a distinct fourth state, not
    a low score, and must stay distinct all the way through to the
    recommendation label.
    """
    if confidence_score is None:
        return "Insufficient"
    if confidence_score >= 70:
        return "High"
    if confidence_score >= 40:
        return "Medium"
    return "Low"


# Exact, literal text from the frozen SRS §7.4 matrix. Do not paraphrase
# or re-derive this from memory -- if it ever needs to change, §1.4
# requires updating the SRS first, then this table to match.
_RECOMMENDATION_MATRIX = {
    ("High", "High"): "Highly Recommended",
    ("High", "Medium"): "Strong Match \u2013 Verify During Interview",
    ("High", "Low"): "Strong Match \u2013 Limited External Evidence",
    ("High", "Insufficient"): "Strong Match \u2013 Verification Pending",

    ("Medium", "High"): "Consider",
    ("Medium", "Medium"): "Consider",
    ("Medium", "Low"): "Potential Match \u2013 Needs Manual Review",
    ("Medium", "Insufficient"): "Potential Match \u2013 Verification Pending",

    ("Low", "High"): "Low Role Match",
    ("Low", "Medium"): "Low Role Match",
    ("Low", "Low"): "Not Recommended",
    ("Low", "Insufficient"): "Low Role Match \u2013 Verification Pending",
}


def generate_recommendation(
    match_score: float,
    confidence_score: float | None
) -> str:
    """
    Returns the recommendation label for a given Match Score and
    Confidence Score, using the exact matrix frozen in SRS §7.4.
    """

    match_band = _match_band(match_score)
    confidence_band = _confidence_band(confidence_score)

    return _RECOMMENDATION_MATRIX[(match_band, confidence_band)]


def update_recommendation(
    db: Session,
    resume_id: int
):
    """
    Updates recommendation inside matching_results.
    """

    result = (
        db.query(MatchingResult)
        .filter(MatchingResult.resume_id == resume_id)
        .first()
    )

    if result is None:
        return None

    # Don't guess a recommendation from incomplete data -- if Match Score
    # hasn't been computed yet (e.g. verification ran before matching, out
    # of the intended order), leave recommendation untouched rather than
    # producing a label that doesn't mean anything yet.
    if result.match_score is None:
        return result

    result.recommendation = generate_recommendation(
        result.match_score,
        result.confidence_score
    )

    db.commit()
    db.refresh(result)

    return result