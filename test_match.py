from app.matching.matcher import calculate_match_score

resume = """
Python developer.
Built REST APIs using FastAPI.
Worked with PostgreSQL.
Docker.
Machine Learning.
"""

job = """
Looking for Python Backend Developer.

Requirements:

Python
FastAPI
Docker
PostgreSQL
"""

score = calculate_match_score(
    resume,
    job
)

print(f"Match Score: {score}%")