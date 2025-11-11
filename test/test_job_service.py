import pytest
from sqlalchemy.orm import sessionmaker, Session
from applog.services.job_service import create_job, get_job_by_id, update_job, delete_job
from applog.database import Base
from applog.models.job_application import JobApplication, ApplicationStatus
from datetime import datetime
from sqlalchemy import create_engine
from typing import Generator
from sqlalchemy.pool import NullPool


@pytest.fixture
def db_session() -> Generator:
    database_url = f"sqlite:///:memory"

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,  # Disables connection pooling
        echo=False,
    )

    Base.metadata.drop_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()

    Base.metadata.create_all(bind=engine)

    yield db
    db.close()

@pytest.fixture
def sample_job_data() -> dict:
    return {
        "company_name": "Imerys",
        "job_title": "Project Manager",
        "job_url": "https://www.indeed.com/jobs/IT/PM/3950195",
        "location": "Geneva, SWZ",
        "status": ApplicationStatus.ACCEPTED,
        "application_date": datetime(2025, 10, 28),
        "salary_range": "CHF 70k - CHF 78k",
        "notes": "I am moving to Switzerland to pursue this career.",
    }


@pytest.fixture
def sample_job_updates() -> dict:
    return {
        "company_name": "Imerys SA",
        "job_title": "Jr IT Project Manager",
        "job_url": "https://www.indeed.com/jobs/IT/PM/58493",
        "location": "Lausanne, SWZ",
        "status": ApplicationStatus.ACCEPTED,
        "application_date": datetime(2025, 10, 29),
        "salary_range": "CHF 72k - CHF 77k",
    }

@pytest.fixture
def sample_partial_updates() -> dict:
    return {
        "job_title": "Jr IT Project Manager",
        "location": "Lausanne, SWZ",
    }

class TestJobService:

    def test_create_job_stores_in_database(self, db_session: Session, sample_job_data: dict) -> None:

        created_job = create_job(db_session, sample_job_data)

        for key, value in sample_job_data.items():
            assert getattr(created_job, key) == sample_job_data[key]

        assert created_job.id is not None
        assert created_job.id in [job.id for job in db_session.query(JobApplication).all()]

    def test_create_job_duplicate_url_rejected(self, db_session: Session, sample_job_data: dict) -> None:
        create_job(db_session, sample_job_data)

        with pytest.raises(ValueError):
            assert create_job(db_session, sample_job_data)

    # todo does not take into account partially empty data
    def test_create_job_empty_data_raises_error(self, db_session: Session) -> None:
        empty_data = {}

        with pytest.raises(ValueError):
            assert create_job(db_session, empty_data)

    @pytest.mark.parametrize("job_id, expected_outcome", [
        (1, True),
        (888, False)
    ])
    def test_get_job_by_id(self, db_session: Session, sample_job_data: dict, job_id: int, expected_outcome: bool) -> None:
        created_job = create_job(db_session, sample_job_data)

        if created_job.id == job_id:
            retrieved = get_job_by_id(db_session, created_job.id)
            assert retrieved.company_name == sample_job_data["company_name"]
            assert retrieved.job_url == sample_job_data["job_url"]
        else:
            assert get_job_by_id(db_session, job_id) is None


    def test_update_job_modifies_fields(self, db_session: Session, sample_job_data: dict, sample_job_updates: dict) -> None:
        created_job = create_job(db_session, sample_job_data)
        updated_job = update_job(db_session, created_job.id, sample_job_updates)

        for key, value in sample_job_updates.items():
            assert getattr(updated_job, key) == sample_job_updates[key]

        assert updated_job.notes == sample_job_data["notes"]

        assert updated_job.id == created_job.id


    def test_update_job_empty_updates_returns_unchanged(self, db_session: Session, sample_job_data: dict) -> None:
        created_job = create_job(db_session, sample_job_data)
        job_updates = dict()
        updated_job = update_job(db_session, created_job.id, job_updates)

        assert updated_job == created_job


    # todo add invalid fields to test
    def test_update_job_using_inexistent_field_is_ignored(self, db_session: Session, sample_job_data: dict, sample_job_updates: dict) -> None:
        created_job = create_job(db_session, sample_job_data)
        updated_job = update_job(db_session, created_job.id, sample_job_updates)

        for key, value in sample_job_updates.items():
            assert getattr(updated_job, key) == sample_job_updates[key]

        assert updated_job.notes == sample_job_data["notes"]


    def test_update_job_partial_updates(self, db_session: Session, sample_partial_updates: dict, sample_job_data: dict) -> None:
        created_job = create_job(db_session, sample_job_data)
        updated_job = update_job(db_session, created_job.id, sample_partial_updates)

        for key, value in sample_partial_updates.items():
            assert getattr(updated_job, key) == sample_partial_updates[key]

        assert updated_job.id == created_job.id


    @pytest.mark.parametrize("job_id, expected_result", [
        (1, True),
        (888, False)
    ])
    def test_delete_entity(self, db_session: Session, sample_job_data: dict, expected_result: bool, job_id: int) -> None:
        created_job = create_job(db_session, sample_job_data)

        if not expected_result:
            assert get_job_by_id(db_session, created_job.id) is not None

        assert delete_job(db_session, job_id) == expected_result

        assert get_job_by_id(db_session, job_id) is None
