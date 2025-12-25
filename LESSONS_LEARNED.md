# Lessons Learned

Technical gotchas, implementation insights, and patterns discovered during development. Organized by importance and frequency of occurrence.

---

# Reflex Var Handling in Templates

**Importance:** CRITICAL | **Frequency:** Very Common

## Issue
**Reflex `Var` objects cannot be used with Python functions that contain conditional checks or type operations on the Var parameter itself.** Vars are reactive proxy objects, not plain values, and conditionals like `if isinstance(var, str)` or `if var` evaluate the Var object, not its runtime value.

## Symptoms
- Python functions return empty strings or default values
- Formatting functions fail silently in `rx.foreach` loops
- Dictionary `.get()` methods return None in templates

## Root Cause
When you pass a Reflex `Var` to a Python function that checks the parameter type or truthiness before converting to string, the check evaluates the Var wrapper object instead of the actual data. For example:
```python
def format_value(val):
    if not val:  # This checks the Var object, not its value!
        return ""
    return str(val).upper()
```

## Solutions

1. **Backend Formatting (Preferred)**
   - Format data in the model's `to_dict()` method or service layer
   - Return pre-formatted fields alongside raw data
   - Example: Add `salary_range_formatted` field in addition to `salary_range`
   - **Use for:** Date formatting, currency formatting, custom transformations

2. **Reflex Built-in Components**
   - Use `rx.moment()` for datetime formatting instead of Python `strftime()`
   - Use `rx.cond()` for conditional rendering instead of Python `if`
   - **Use for:** Dates, times, conditional UI elements

3. **Direct Dictionary Access in Templates**
   - Use `note["field"]` instead of `note.get("field", "")` in `rx.foreach` loops
   - The `.get()` method doesn't work reliably with Vars
   - **Use for:** Accessing nested dictionary fields in foreach loops

4. **String Conversion Without Conditionals**
   - If you must use Python functions, convert to string immediately without checking:
   ```python
   def format_value(val):
       str_val = str(val)  # Convert first, no conditionals on the Var parameter
       if str_val == "":   # Now check the string value
           return ""
       return str_val.upper()
   ```

## Common Operations Affected
- **Date/time formatting** → Use `rx.moment()` or backend formatting
- **Currency/number formatting** → Backend formatting in `to_dict()`
- **String manipulation with validation** → Backend formatting or immediate string conversion
- **Conditional rendering** → Use `rx.cond()` instead of Python `if`
- **Dictionary field access in loops** → Use `dict["key"]` not `dict.get("key")`

## Key Takeaway
**When working with Reflex templates and reactive data, prefer backend formatting or Reflex-native components over Python utility functions.** This avoids Var serialization issues and improves maintainability.

---

# Actual Data Flow (SQLAlchemy/Reflex Web Apps)

**Importance:** CRITICAL | **Frequency:** Very Common

## Key Misconception
Data is NOT loaded once at startup and flushed back on exit. Each CRUD operation writes to the database immediately.

## Corrected Flow

### 1. User opens app
- Reflex initializes State(rx.State) [per session]
- State calls service layer (e.g., `job_service.get_all_jobs()`)
- Service opens DB session
- Queries DB → returns List[JobApplication] (ORM objects)
- Service converts to dicts via `to_dict()` (serialization)
- Returns to State
- State stores in `self.jobs`
- DB session closes

### 2. User searches/filters
- `State.search_query` updates
- `State.filtered_jobs` computed property re-runs (in-memory filtering of loaded data)
- UI updates reactively

### 3. User creates new job
- UI form submits data
- State calls `job_service.create_job(data)`
- Service opens DB session
- Creates JobApplication object
- `session.add(job)` + `session.commit()` → **WRITES TO DB IMMEDIATELY**
- DB session closes
- State refreshes jobs list (calls `get_all_jobs()` again)
- UI updates

### 4. User deletes job
- State calls `job_service.delete_job(job_id)`
- Service opens DB session
- Queries for job → `session.delete(job)` → `session.commit()` → **WRITES IMMEDIATELY**
- DB session closes
- State refreshes jobs list
- UI updates

---

# Key Terminology & Concepts

**Importance:** CRITICAL | **Frequency:** Very Common (Reference Material)

## Database & ORM Terminology

| Term                            | Meaning                                                                       | Example in This Project                        |
|---------------------------------|-------------------------------------------------------------------------------|------------------------------------------------|
| ORM (Object-Relational Mapping) | Framework that maps database tables to Python classes                        | SQLAlchemy                                     |
| Model / Entity Class            | The SQLAlchemy class that represents a DB table                               | `JobApplication(Base)`                         |
| Entity / Model Instance         | An instance of a model representing one DB row                                | `job = JobApplication(company_name="Google")`  |
| Session                         | Database connection context that tracks changes and manages transactions      | `SessionLocal()` from database.py              |
| Persistence                     | Saving data to permanent storage (database)                                   | `session.commit()`                             |
| Serialization                   | Converting Python objects to dicts/JSON                                       | `job.to_dict()`                                |
| Deserialization                 | Converting dicts/JSON back to Python objects                                  | Constructor: `JobApplication(**data)`          |
| DTO (Data Transfer Object)      | Plain data structure for passing data between layers                          | `{"id": 1, "company_name": "Tech Corp"}`       |
| Repository / Service Layer      | Business logic layer that handles CRUD operations                             | `job_service.py`                               |
| State Management                | Reflex's reactive system that holds UI state and triggers updates             | `State(rx.State)`                              |
| Transaction                     | Atomic unit of database work                                                  | commit = save permanently, rollback = undo     |

## Quick Reference Quiz

**Given this code:**
```python
class JobApplication(Base):
    company_name = Column(String)

tech_job = JobApplication(company_name="Google")
job_data = tech_job.to_dict()

session.add(tech_job)
session.commit()
```

**Questions:**
1. What is `JobApplication`?
2. What is `tech_job`?
3. What is `job_data`?
4. What does the session code do?

**Answers:**
1. Model (entity class)
2. Entity (model instance / ORM object)
3. DTO (plain dict for serialization)
4. Commits the transaction / Persists the entity (writes to DB permanently)

---

# Component Organization: Type vs. Domain Trade-off

**Importance:** CRITICAL | **Frequency:** Very Common

## The Fundamental Problem
**You cannot optimize for multiple access patterns with a single hierarchy.** When organizing components, you face an inherent trade-off:

- **Type-first** (`_button_*`, `_form_*`, `_input_*`) → Easy to find all buttons, inputs, etc.
- **Domain-first** (`_template_*`, `_note_*`, `_job_*`) → Easy to find all components for a feature

This is an **unsolvable hurdle** in single-hierarchy systems. You can only pick one primary organization axis.

## Solution: Hybrid Naming Convention

For single-file components (before splitting into modules), use hybrid naming:

```python
# Type prefix for grouping by component kind
_button_save
_button_cancel
_button_template_selector

# Domain prefix for grouping by feature
_template_selector_list
_template_search_input
_template_settings_tooltip

# Formatting dictionaries always prefixed
_formatting_button_section
_formatting_template_list
```

**Why this works:**
- `_button_*` groups all buttons → Type-based access
- `_template_*` groups template components → Domain-based access
- Both accessible via IDE search (Cmd+T / Cmd+Shift+O)
- Scales well up to ~100 components per file

## Future: Directory Structure

When splitting into modules (100+ components):
- Use **directories for feature domains**: `jobs/`, `templates/`, `shared/`
- Use **filenames for component types**: `buttons.py`, `forms.py`, `dialogs.py`
- Use **barrel exports** (`__init__.py`) to provide both access patterns

**Example:**
```
components/jobs/detail/
├── buttons.py          # All detail page buttons
├── forms.py            # All form components
├── templates.py        # Template-related components
└── __init__.py         # Exports for both access patterns
```

## Key Takeaway
Don't over-engineer early. Hybrid naming in flat files → Directory structure when needed (100+ components) → Component catalog/Storybook at scale (500+ components).

**Full details**: See README.md "Component Organization" section for comprehensive patterns, barrel export examples, and production best practices.

---

# SQLite In-Memory Database Persistence in Tests

**Importance:** CRITICAL | **Frequency:** Occasional (Testing-specific)

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

# Archive Feature Pattern: Computed Variables for Data Filtering

**Importance:** MEDIUM | **Frequency:** Rare (Feature-specific)

## Pattern: Use `@rx.var` for Logical Data Categories

When you need to split data into logical categories (active vs. archived, public vs. private, etc.), use computed variables instead of manual filtering:

```python
@rx.var
def active_jobs(self) -> List[Dict]:
    """Jobs excluding Rejected/Withdrawn."""
    return [j for j in self.jobs if j["status"] not in ["Rejected", "Withdrawn"]]

@rx.var
def archived_jobs(self) -> List[Dict]:
    """Jobs with Rejected/Withdrawn status."""
    return [j for j in self.jobs if j["status"] in ["Rejected", "Withdrawn"]]
```

## Why This Works
- **Reactive**: Reflex tracks `self.jobs` as dependency
- **Automatic**: When `jobs` changes, computed vars auto-update
- **No manual refresh**: No need to call update functions
- **Separation of concerns**: Data transformation separate from UI logic

## Key Principles
1. Don't modify source data (`self.jobs`) - always filter it
2. Use `@rx.var` decorator for reactivity
3. Access as property (`State.active_jobs`), not function (`State.active_jobs()`)
4. Chain computed vars: `filtered_active_jobs` can filter `active_jobs`

**Full Tutorial**: See `docs/tutorials/archive-feature.md` for complete step-by-step implementation guide with testing checklist and common mistakes.
