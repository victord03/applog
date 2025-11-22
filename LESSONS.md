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

---

# Archive Feature Implementation Guide

## Feature Overview
Archive jobs with "Rejected" or "Withdrawn" status to keep the main page clean. Users can view archived jobs on a separate `/archive` page.

**Difficulty:** 1/3 (Simple - great practice with `@rx.var`)

## Why This Is Good @rx.var Practice
- Learn to create computed variables that filter data
- Understand dependency tracking (when `self.jobs` changes, computed vars auto-update)
- Practice the proper Reflex pattern for data transformation
- See how computed vars eliminate manual refresh logic

---

## Implementation Steps

### Step 1: Create Computed Variables for Active/Archived Jobs

**Location:** `applog/applog.py` in the `State` class (after `selected_job_notes`)

**Concept:** Split `self.jobs` into two categories based on status

**Code Pattern:**
```python
@rx.var
def active_jobs(self) -> List[Dict]:
    """Jobs excluding Rejected/Withdrawn."""
    # Return list comprehension filtering self.jobs
    # Exclude jobs where status is "Rejected" or "Withdrawn"
    pass

@rx.var
def archived_jobs(self) -> List[Dict]:
    """Jobs with Rejected/Withdrawn status."""
    # Return list comprehension filtering self.jobs
    # Include ONLY jobs where status is "Rejected" or "Withdrawn"
    pass
```

**Hints:**
- Use list comprehension: `[j for j in self.jobs if ...]`
- Check `j["status"]` against the strings "Rejected" and "Withdrawn"
- Use `not in` for active_jobs, `in` for archived_jobs

---

### Step 2: Update Main Page to Use Active Jobs Only

**Location:** `applog/applog.py` in `filtered_jobs` computed var (around line 152)

**Concept:** Change the starting point for filtering from all jobs to only active jobs

**Current Code:**
```python
@rx.var
def filtered_jobs(self) -> List[Dict]:
    """Get filtered jobs based on search and filter criteria."""
    result = self.jobs  # ← Change this line
    # ... rest of filtering logic
```

**Change To:**
```python
result = self.active_jobs  # Now starts with active jobs only
```

**Also Update:** The `total_jobs_count` computed var (around line 147)
```python
@rx.var
def total_jobs_count(self) -> int:
    """Get total number of job applications."""
    return len(self.active_jobs)  # Changed from self.jobs
```

---

### Step 3: Create Archive Page

**Location:** `applog/applog.py` - new function after `index()` function (around line 1670)

**Concept:** Copy the `index()` function and modify it to show archived jobs

**Steps:**
1. Find the `def index() -> rx.Component:` function
2. Copy the entire function (from `def` to the closing `)`)
3. Paste it below and rename to `def archive_page() -> rx.Component:`
4. Update the title/heading:
   - Change `"AppLog"` to `"Job Archive"`
   - Change `"Track your job applications"` to `"Rejected and withdrawn applications"`
5. Replace the "Add Job" button with a "Back to Active Jobs" button:
   ```python
   rx.link(
       rx.button(
           "← Back to Active Jobs",
           size="3",
           variant="solid",
       ),
       href="/",
   ),
   ```
6. Update the job counter to show archived count:
   ```python
   f"Archived: {State.total_archived_count}"
   ```
7. The `job_list()` component automatically uses `filtered_jobs`, so you'll need to...

**Wait - Better Approach:**
Create a new computed var for `filtered_archived_jobs` that filters archived jobs based on search/company/location. This is the proper Reflex way!

```python
@rx.var
def filtered_archived_jobs(self) -> List[Dict]:
    """Get filtered archived jobs based on search and filter criteria."""
    result = self.archived_jobs  # Start with archived instead of active
    # Copy the same filtering logic from filtered_jobs
    # (search_query, selected_company, selected_status, selected_location)
    pass
```

Then create a new `archive_job_list()` component that uses `State.filtered_archived_jobs` instead of `State.filtered_jobs`.

**Alternative (Simpler):** Just create a basic archive page without filters initially. You can add filters later.

---

### Step 4: Add Total Archived Count Computed Var

**Location:** After `total_jobs_count` in State class

```python
@rx.var
def total_archived_count(self) -> int:
    """Get total number of archived job applications."""
    return len(self.archived_jobs)
```

---

### Step 5: Add Archive Navigation Button

**Location:** Main page header where "Templates" button is (around line 1625)

**Find this code:**
```python
rx.hstack(
    rx.link(
        rx.button(
            "Templates",
            size="3",
            variant="soft",
        ),
        href="/templates",
    ),
    rx.link(
        rx.button(
            "+ Add Job",
            size="3",
            variant="solid",
        ),
        href="/add-job",
    ),
    spacing="3",
),
```

**Add Archive button:**
```python
rx.hstack(
    rx.link(
        rx.button(
            f"Archive ({State.total_archived_count})",
            size="3",
            variant="soft",
        ),
        href="/archive",
    ),
    rx.link(
        rx.button(
            "Templates",
            size="3",
            variant="soft",
        ),
        href="/templates",
    ),
    rx.link(
        rx.button(
            "+ Add Job",
            size="3",
            variant="solid",
        ),
        href="/add-job",
    ),
    spacing="3",
),
```

---

### Step 6: Register Archive Route

**Location:** Bottom of `applog/applog.py` where routes are registered (around line 1680)

**Find:**
```python
app.add_page(index, on_load=State.load_index_page)
app.add_page(add_job, route="/add-job", on_load=State.load_add_job_page)
app.add_page(job_detail, route="/job/[job_id]", on_load=State.load_job)
app.add_page(templates_page, route="/templates", on_load=State.load_templates_page)
```

**Add:**
```python
app.add_page(archive_page, route="/archive", on_load=State.load_index_page)
```

**Note:** We reuse `load_index_page` since it just loads jobs from DB - same data source!

---

## Testing Checklist

After implementation, test these scenarios:

1. **Main Page Shows Only Active Jobs**
   - [ ] Jobs with "Applied", "Screening", "Interview", "Offer" statuses appear
   - [ ] Jobs with "Rejected" or "Withdrawn" do NOT appear
   - [ ] Counter shows correct number of active jobs

2. **Archive Page Shows Only Archived Jobs**
   - [ ] Navigate to `/archive`
   - [ ] Only "Rejected" and "Withdrawn" jobs appear
   - [ ] Counter shows correct number of archived jobs

3. **Status Change Moves Jobs Between Pages**
   - [ ] Change a job status to "Rejected" → disappears from main page
   - [ ] Go to archive → the job appears there
   - [ ] Change archived job back to "Applied" → disappears from archive
   - [ ] Go to main page → the job reappears

4. **Navigation Works**
   - [ ] "Archive" button shows correct count
   - [ ] Clicking Archive button goes to `/archive`
   - [ ] "Back to Active Jobs" button returns to `/`

5. **Search/Filters Work (If Implemented)**
   - [ ] Search works on archive page
   - [ ] Company/location filters work on archive page

---

## Common Mistakes to Avoid

1. **Don't modify `self.jobs` directly** - It's the source data. Always filter it with computed vars.

2. **Don't forget to update `total_jobs_count`** - It should count active jobs only, not all jobs.

3. **Don't call `.filter()` on lists** - Use list comprehension instead: `[j for j in list if condition]`

4. **Don't forget the `@rx.var` decorator** - Without it, the function won't be reactive.

5. **Don't access `State.active_jobs()` with parentheses** - It's a property, use `State.active_jobs`

---

## Learning Outcomes

After completing this feature, you'll understand:

- ✅ How to create computed variables that filter data
- ✅ How computed vars automatically update when dependencies change
- ✅ How to organize data into logical categories using `@rx.var`
- ✅ Why computed vars are better than calling functions in the UI
- ✅ How Reflex tracks dependencies (when you use `self.jobs`, Reflex knows to re-run when jobs changes)
- ✅ The pattern for creating new pages that share state

---

## Bonus: Add Filtering to Archive Page

Once basic archive works, add search/filter by:

1. Creating `filtered_archived_jobs` computed var (same logic as `filtered_jobs` but starting with `self.archived_jobs`)
2. Creating `archived_job_list()` component that uses `State.filtered_archived_jobs`
3. Adding the same search bar and filter sidebar to archive page

This is optional but great practice!