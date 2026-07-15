from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model only once
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def calculate_match_score(
    resume_text: str,
    job_description: str
):
    """
    Calculates semantic similarity
    between resume and job description.
    """

    embeddings = model.encode(
        [resume_text, job_description]
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return round(similarity * 100, 2)