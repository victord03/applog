from sqlalchemy.orm import Session
from applog.models.job_application import JobApplication

def validate_fields(job_data: dict) -> None:
    """Validate that dictionary is not empty and all field names exist in JobApplication model.

    Args:
        job_data: Dictionary containing job application field names and values.

    Raises:
        ValueError: If dictionary is empty or contains invalid field names.
    """
    if not job_data:  # empty dict
        raise ValueError("Dictionary passed is empty (no key values).")

    for key in job_data:
        if not hasattr(JobApplication, key):  # field not in JobApplication class
            raise ValueError(f"Field {key} does not exist. Maybe typo?")


def create_job(session: Session, job_data: dict) -> JobApplication:
    """Create a new job application entry in the database.

    Args:
        session: SQLAlchemy database session.
        job_data: Dictionary containing job application data (company_name, job_title, job_url, etc.).

    Returns:
        The created JobApplication object with assigned ID.

    Raises:
        ValueError: If job_data is invalid or job_url already exists in database.
    """
    validate_fields(job_data)  # Checks for 1. Empty dict, 2. Invalid fields. Raises ValueError.

    existing = (
        session.query(JobApplication).filter_by(job_url=job_data["job_url"]).first()
    )

    if existing:  # job_url is a way to avoid duplicate entries. If it exists, the creation is aborted.
        raise ValueError(f"Job with the URL {job_data['job_url']} already exists.")

    job = JobApplication(**job_data)

    try:
        session.add(job)
        session.commit()
        session.refresh(job)
    except Exception:
        session.rollback()
        raise

    return job


def get_job_by_id(session: Session, job_id: int) -> JobApplication | None:
    """Retrieve a job application by its ID.

    Args:
        session: SQLAlchemy database session.
        job_id: The ID of the job application to retrieve.

    Returns:
        JobApplication object if found, None otherwise.
    """
    return session.get(JobApplication, job_id)


def update_job(
    session: Session, job_id: int, job_updates: dict
) -> JobApplication | None:
    """Update an existing job application with new field values.

    Args:
        session: SQLAlchemy database session.
        job_id: The ID of the job application to update.
        job_updates: Dictionary containing fields to update and their new values.

    Returns:
        Updated JobApplication object if job_id exists, None otherwise.

    Raises:
        ValueError: If job_updates is invalid (empty or contains invalid field names).
    """
    validate_fields(job_updates)  # Checks for 1. Empty dict, 2. Invalid fields. Raises ValueError.

    existing_job = get_job_by_id(session, job_id)

    if existing_job is None:  # This entity id does not exist
        return None

    for key, value in job_updates.items():
        setattr(existing_job, key, value)

    try:
        session.commit()
        session.refresh(existing_job)
    except Exception:
        session.rollback()
        raise

    return existing_job


def delete_job(session: Session, job_id: int) -> bool:
    """Delete a job application from the database.

    Args:
        session: SQLAlchemy database session.
        job_id: The ID of the job application to delete.

    Returns:
        True if deletion succeeded, False if job_id doesn't exist.
    """
    existing_job = get_job_by_id(session, job_id)

    if existing_job is None:
        return False

    try:
        session.delete(existing_job)
        session.commit()
    except Exception:
        session.rollback()
        raise

    return True
