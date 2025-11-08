from sqlalchemy.orm import Session
from applog.models.job_application import JobApplication

def create_job(session: Session, job_data: dict) -> JobApplication:

    if len(list(job_data.keys())) == 0:
        raise ValueError("Dictionary passed is empty (no key values).")

    job = JobApplication(**job_data)

    # session.query(f"FROM JobApplication SELECT * WHERE job_url is {job_data['job_url']}")

    session.add(job)
    session.commit()
    session.refresh(job)

    return job


def get_job_by_id(session: Session, job_id: int) -> JobApplication | None:
    return session.get(JobApplication, job_id)


def update_job(session: Session, job_id: int, job_updates: dict) -> JobApplication | None:

    existing_job = get_job_by_id(session, job_id)

    if existing_job is None or len(list(existing_job.keys())) == 0:
        return None

    for key, value in job_updates.items():
        if hasattr(existing_job, key):
            setattr(existing_job, key, value)

    session.commit()
    session.refresh(existing_job)

    return existing_job


def delete_job(session: Session, job_id: int) -> bool:

    existing_job = get_job_by_id(session, job_id)

    if existing_job is None:
        return False

    session.delete(existing_job)
    session.commit()

    return True

