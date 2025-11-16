import pytest
from sqlalchemy.orm import sessionmaker, Session
from applog.services.job_service import (
    create_job,
    get_job_by_id,
    get_job_by_url,
    update_job,
    delete_job,
    add_note
)
from applog.database import Base
from applog.models.job_application import JobApplication, ApplicationStatus
from datetime import datetime
from sqlalchemy import create_engine
from typing import Generator
from sqlalchemy.pool import NullPool
from unittest.mock import patch


@pytest.fixture
def db_session() -> Generator:
    database_url = "sqlite:///:memory"

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

    yield db  # Pytest fixture already calls the next() on the returned object. Would not work outside pytest.fixture
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
        "notes": [
            {
                "timestamp": "2025-11-16T00:00:00",
                "note": "I am moving to Switzerland to pursue this career."
            }
        ],
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


class TestCreate:
    def test_create_job_stores_in_database(
        self, db_session: Session, sample_job_data: dict
    ) -> None:
        created_job = create_job(db_session, sample_job_data)

        for key, value in sample_job_data.items():
            assert getattr(created_job, key) == sample_job_data[key]

        assert created_job.id is not None
        assert created_job.id in [
            job.id for job in db_session.query(JobApplication).all()
        ]

    def test_create_job_duplicate_url_rejected(
        self, db_session: Session, sample_job_data: dict
    ) -> None:
        create_job(db_session, sample_job_data)

        with pytest.raises(ValueError):
            assert create_job(db_session, sample_job_data)

    def test_create_job_empty_data_raises_error(self, db_session: Session) -> None:
        empty_data = {}

        with pytest.raises(ValueError):
            assert create_job(db_session, empty_data)

    @pytest.mark.parametrize(
        "sample_job",
        [
            {"company_name": "Imerys SA", "invalid_field": "Some random value"},
            {"invalid_field": "Some random value"},
        ],
    )
    def test_create_with_invalid_field_raises_error(
        self,
        db_session: Session,
        sample_job: dict,
    ) -> None:
        with pytest.raises(ValueError):
            create_job(db_session, sample_job)

    def test_create_job_runs_exception_on_commit_fails(self, db_session: Session, sample_job_data: dict) -> None:
        entities_count_before = len(db_session.query(JobApplication).all())

        with patch.object(db_session, 'commit', side_effect=Exception('DB error')):
            with pytest.raises(Exception):
                create_job(db_session, sample_job_data)

        entities_count_after = len(db_session.query(JobApplication).all())
        assert entities_count_before == entities_count_after


    def test_create_job_with_non_default_status(self, db_session: Session):
        job_data = {
            "company_name": "Test Corp",
            "job_title": "Developer",
            "job_url": "https://test.com/job",
            "status": ApplicationStatus.SCREENING  # Non-default
        }
        created_job = create_job(db_session, job_data)
        assert created_job.status == ApplicationStatus.SCREENING

    # todo Minimize duplicates of the same job offer from different sites (e.g. LinkedIn link then indeed link)
    def test_find_similar_jobs_detects_duplicate_from_different_domain(self):
        ...

class TestRead:

    def test_get_job_by_id_returns_job_when_exists(
        self,
        db_session: Session,
        sample_job_data: dict,
    ) -> None:
        created_job = create_job(db_session, sample_job_data)

        retrieved = get_job_by_id(db_session, created_job.id)
        assert retrieved == created_job

    def test_get_job_by_id_returns_none_when_not_found(self, db_session: Session) -> None:
        job_id = 888
        assert get_job_by_id(db_session, job_id) is None

    def test_get_job_by_url(self, db_session: Session, sample_job_data: dict) -> None:
        created_job = create_job(db_session, sample_job_data)
        assert get_job_by_url(db_session, created_job.job_url) == created_job

    def test_get_job_by_url_returns_none_when_not_found(self, db_session: Session) -> None:
        job_url = "https://www.linkedin.com/jobs/a9304/project-manager-aFJ103j401"
        assert get_job_by_url(db_session, job_url) is None

    def test_get_job_by_url_with_trailing_slash(self, db_session: Session, sample_job_data: dict) -> None:
        # If URL stored as "example.com/job" but searched "example.com/job/"
        created_job = create_job(db_session, sample_job_data)
        trailing_slash_url = "https://www.indeed.com/jobs/IT/PM/3950195/"

        assert get_job_by_url(db_session, trailing_slash_url) == created_job

    @pytest.mark.parametrize("capped_url",[
        "https://WWW.INDEED.COM/jobs/IT/PM/3950195/", # domain caps
        "HTTPS://WWW.INDEED.COM/jobs/IT/PM/3950195/", # domain + scheme caps
        "HTTPS://www.indeed.com/jobs/IT/PM/3950195/", # scheme caps
        "https://www.INDEED.COM/jobs/IT/PM/3950195/" # mixed caps (e.g. emulating scraping issues)
    ])
    def test_get_job_by_url_case_sensitivity(self, db_session: Session, sample_job_data: dict, capped_url: str) -> None:
        # "HTTPS://EXAMPLE.COM" vs "https://example.com"
        # URLs are case-sensitive in path, not domain
        created_job = create_job(db_session, sample_job_data)
        assert get_job_by_url(db_session, capped_url) == created_job

    def test_get_job_by_url_empty_string(self, db_session: Session, sample_job_data: dict) -> None:
        # Edge case: what happens with ""
        create_job(db_session, sample_job_data)
        assert get_job_by_url(db_session, "") is None



class TestUpdate:

    def test_update_job_modifies_fields(
        self, db_session: Session, sample_job_data: dict, sample_job_updates: dict
    ) -> None:
        created_job = create_job(db_session, sample_job_data)
        updated_job = update_job(db_session, created_job.id, sample_job_updates)

        for key, value in sample_job_updates.items():
            assert getattr(updated_job, key) == value

        assert updated_job.notes == sample_job_data["notes"]

        assert updated_job.id == created_job.id

    @pytest.mark.parametrize(
        "sample_updates",
        [
            {"company_name": "Imerys SA", "invalid_field": "Some random value"},
            {"invalid_field": "Some random value"},
            {},
        ],
    )
    def test_update_job_invalid_field_or_empty_dict_raises_error(
        self,
        db_session: Session,
        sample_job_updates: dict,
        sample_updates: dict,
    ) -> None:
        created_job = create_job(db_session, sample_job_updates)

        with pytest.raises(ValueError):
            update_job(db_session, created_job.id, sample_updates)

    def test_update_job_partial_updates(
        self, db_session: Session, sample_partial_updates: dict, sample_job_data: dict
    ) -> None:
        created_job = create_job(db_session, sample_job_data)
        updated_job = update_job(db_session, created_job.id, sample_partial_updates)

        for key, value in sample_partial_updates.items():
            assert getattr(updated_job, key) == sample_partial_updates[key]

        assert updated_job.id == created_job.id

    def test_try_updating_passing_nonexistent_id(
        self, db_session: Session, sample_job_updates: dict, sample_job_data: dict
    ) -> None:
        create_job(db_session, sample_job_data)
        invalid_id = 999

        assert update_job(db_session, invalid_id, sample_job_updates) is None


    def test_update_job_runs_exception_on_commit_fail(self, db_session: Session, sample_job_data: dict, sample_job_updates: dict) -> None:
        created_job = create_job(db_session, sample_job_data)
        with patch.object(db_session, 'commit', side_effect=Exception('DB error')):
            with pytest.raises(Exception):
                update_job(db_session, created_job.id, sample_job_updates)

        assert get_job_by_id(db_session, created_job.id) == created_job

class TestDelete:
    @pytest.mark.parametrize("job_id, expected_result", [(1, True), (888, False)])
    def test_delete_entity(
        self,
        db_session: Session,
        sample_job_data: dict,
        expected_result: bool,
        job_id: int,
    ) -> None:
        created_job = create_job(db_session, sample_job_data)

        if expected_result:
            assert get_job_by_id(db_session, created_job.id) is not None
        else:
            assert get_job_by_id(db_session, job_id) is None

        assert delete_job(db_session, job_id) == expected_result

        assert get_job_by_id(db_session, job_id) is None


    def test_delete_job_runs_exception_on_commit_fail(self, db_session: Session, sample_job_data) -> None:
        created_job = create_job(db_session, sample_job_data)
        with patch.object(db_session, 'commit', side_effect=Exception('DB error')):
            with pytest.raises(Exception):
                delete_job(db_session, created_job.id)

        assert get_job_by_id(db_session, created_job.id) == created_job


class TestNotes:

    def test_add_note_appends_to_existing_notes(self, db_session, sample_job_data):
        # Create job with initial note
        created_job = create_job(db_session, sample_job_data)
        initial_count = len(created_job.notes)

        # Add second note
        updated_job = add_note(db_session, created_job.id, "Follow-up scheduled")

        # Verify:
        # - List grew by 1
        assert len(updated_job.notes) == initial_count + 1
        # - Latest note has correct text
        assert updated_job.notes[-1]["note"] == "Follow-up scheduled"
        # - Latest note has timestamp
        assert "timestamp" in updated_job.notes[-1]

    def test_add_note_to_nonexistent_job(self, db_session):
        # Should return None
        assert add_note(db_session, 999, "test") is None

    def test_add_note_to_job_with_no_notes(self, db_session):
        # Create job without notes field
        job_data = {
          "company_name": "Test",
          "job_title": "Developer",
          "job_url": "https://example.com/job"
        }
        created_job = create_job(db_session, job_data)

        # Add first note
        updated_job = add_note(db_session, created_job.id, "First note")

        # Verify list created correctly
        assert len(updated_job.notes) == 1
        assert updated_job.notes[0]["note"] == "First note"