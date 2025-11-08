# Actual Data Flow (for web apps with SQLAlchemy/Reflex)

  Key Misconception: Data is NOT loaded once at startup and flushed back on exit. Each CRUD operation writes to the
  database immediately.

  Corrected Flow:

  1. User opens app
     → Reflex initializes State(rx.State) [per session]
     → State calls service layer (e.g., job_service.get_all_jobs())
     → Service opens DB session
     → Queries DB → returns List[JobApplication] (ORM objects)
     → Service converts to dicts via to_dict() (serialization)
     → Returns to State
     → State stores in self.jobs
     → DB session closes

  2. User searches/filters
     → State.search_query updates
     → State.filtered_jobs computed property re-runs (in-memory filtering of loaded data)
     → UI updates reactively

  3. User creates new job
     → UI form submits data
     → State calls job_service.create_job(data)
     → Service opens DB session
     → Creates JobApplication object
     → session.add(job) + session.commit() → WRITES TO DB IMMEDIATELY
     → DB session closes
     → State refreshes jobs list (calls get_all_jobs() again)
     → UI updates

  4. User deletes job
     → State calls job_service.delete_job(job_id)
     → Service opens DB session
     → Queries for job → session.delete(job) → session.commit() → WRITES IMMEDIATELY
     → DB session closes
     → State refreshes jobs list
     → UI updates

  ---
  # Key Terminology

  | Term                            | Meaning                                                                       |
  |---------------------------------|-------------------------------------------------------------------------------|
  | ORM (Object-Relational Mapping) | Framework that maps database tables to Python classes (SQLAlchemy)            |
  | Model                           | The SQLAlchemy class that represents a DB table (JobApplication)              |
  | Entity                          | An instance of a model representing one DB row                                |
  | Session                         | Database connection context that tracks changes and manages transactions      |
  | Persistence                     | Saving data to permanent storage (database)                                   |
  | Serialization                   | Converting Python objects to dicts/JSON (.to_dict())                          |
  | Deserialization                 | Converting dicts/JSON back to Python objects                                  |
  | DTO (Data Transfer Object)      | Plain data structure for passing data between layers (what to_dict() returns) |
  | Repository / Service Layer      | Business logic layer that handles CRUD operations (job_service.py)            |
  | State Management                | Reflex's reactive system that holds UI state and triggers updates             |
  | Transaction                     | Atomic unit of database work (commit = save permanently, rollback = undo)     |


# Terminology Summary for This Project

  | What It Is                 | Correct Term                 | Example                                |
  |----------------------------|------------------------------|----------------------------------------|
  | SQLAlchemy itself          | ORM framework                | from sqlalchemy import ...             |
  | JobApplication(Base) class | Model / Entity class         | The class definition                   |
  | job = JobApplication(...)  | Entity / Model instance      | One job posting object                 |
  | job.to_dict() result       | DTO (dict)                   | {"id": 1, "company_name": "Tech Corp"} |
  | One database row           | Entity / Record / Row        | All data for job #1                    |
  | Saving changes             | Commit transaction / Persist | session.commit()                       |


# Quiz to Test Understanding

  Given this code:
1. What is JobApplication?
class JobApplication(Base):
    company_name = Column(String)

2. What is tech_job?
tech_job = JobApplication(company_name="Google")

3. What is job_data?
job_data = tech_job.to_dict()

4. What does this do?
session.add(tech_job)
session.commit()

  Answers:
  1. Model (entity class)
  2. Entity (model instance / ORM object)
  3. DTO (plain dict for serialization)
  4. Commits the transaction / Persists the entity (writes to DB permanently)


---
# SQLite In-Memory Database Persistence in Tests

## Issue Encountered
When using `sqlite:///:memory:` databases for pytest fixtures, SQLAlchemy's `Base.metadata` object acts as a **global singleton** that persists across test runs within the same Python process. Calling `Base.metadata.clear()` removes table definitions from the metadata registry but does NOT drop existing tables from the database. This causes:
- Tables to exist in the database but not in metadata
- `create_all()` to skip table creation (metadata is empty)
- Old test data to persist across test runs
- `IntegrityError` on UNIQUE constraints from previous test data

## Technical Root Cause
SQLite in-memory databases can persist when using connection pooling or when the same connection/engine is reused. Combined with SQLAlchemy's global metadata registry, this creates a state mismatch where the database contains tables and data that metadata no longer tracks.

## Solution
Always call `Base.metadata.drop_all(bind=engine)` **before** `Base.metadata.create_all(bind=engine)` in test fixtures:

```python
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", poolclass=NullPool)
    Base.metadata.drop_all(bind=engine)  # Explicitly drop all tables
    Base.metadata.create_all(bind=engine)  # Create fresh tables
    # ... rest of fixture
```

## When This Occurs
- Using `declarative_base()` from SQLAlchemy with shared `Base` across modules
- Running multiple tests in same pytest session
- Using in-memory SQLite databases for testing
- Connection pooling enabled (default behavior)

## Prevention
1. **Always use `drop_all()` before `create_all()`** in test fixtures
2. Use `NullPool` to disable connection pooling: `create_engine(..., poolclass=NullPool)`
3. Consider fixture scope - use `scope="function"` for test isolation
4. Never use `Base.metadata.clear()` - it breaks the metadata/database sync