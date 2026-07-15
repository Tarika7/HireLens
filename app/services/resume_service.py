import os
import uuid
import shutil

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.utils.pdf_extractor import extract_text_from_pdf
from app.ai.parser import parse_resume
from app.services.parser_service import save_parsed_resume

UPLOAD_DIR = "uploads/resumes"


def save_resume(
    db: Session,
    recruiter_id: int,
    job_id: int,
    file: UploadFile
):
    """
    Save uploaded resume,
    extract text,
    parse resume,
    and store parsed information.
    """

    # -----------------------------
    # Create upload folder
    # -----------------------------
    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True
    )

    # -----------------------------
    # Generate unique filename
    # -----------------------------
    extension = file.filename.split(".")[-1]

    unique_filename = f"{uuid.uuid4()}.{extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )

    # -----------------------------
    # Save file
    # -----------------------------
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    # -----------------------------
    # Extract PDF text
    # -----------------------------
    text = extract_text_from_pdf(file_path)

    # -----------------------------
    # Create Resume record
    # -----------------------------
    resume = Resume(
        recruiter_id=recruiter_id,
        job_id=job_id,
        original_filename=file.filename,
        stored_filename=unique_filename,
        file_path=file_path,
        raw_text=text,          # ⭐ NEW
        parsing_status="Pending"
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    # -----------------------------
    # Parse Resume
    # -----------------------------
    parsed_data = parse_resume(text)

    # -----------------------------
    # Save Parsed Resume
    # -----------------------------
    save_parsed_resume(
        db=db,
        resume=resume,
        parsed_data=parsed_data
    )

    # -----------------------------
    # Update Parsing Status
    # -----------------------------
    resume.parsing_status = "Completed"

    db.commit()
    db.refresh(resume)

    return resume