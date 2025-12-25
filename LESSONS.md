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

# Reflex Var Handling in Templates

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

---

# Component Organization Strategies: Type vs. Domain

## The Fundamental Problem

**You cannot optimize for multiple access patterns with a single hierarchy.** When organizing components, you face an inherent trade-off:

- **Component Type First** (`_button_*`, `_form_*`, `_input_*`) - Easy to find all buttons, inputs, etc.
- **Feature Domain First** (`_template_*`, `_note_*`, `_job_*`) - Easy to find all components for a feature

This is an **unsolvable hurdle** in single-hierarchy systems. You can only pick one primary organization axis.

---

## Solution 1: Directory Structure + Index Files (Most Common)

Use **directories for feature domains** and **filenames for component types**.

### Example Structure:
```
components/
├── jobs/
│   ├── detail/
│   │   ├── buttons.py          # All detail page buttons
│   │   ├── forms.py            # All detail page forms
│   │   ├── templates.py        # Template-related components
│   │   ├── dialogs.py          # Dialog components
│   │   └── __init__.py         # Barrel exports
│   ├── list/
│   │   ├── cards.py
│   │   └── filters.py
│   └── __init__.py
├── shared/
│   ├── buttons.py               # Shared button components
│   ├── inputs.py
│   └── status_badge.py
└── templates/
    ├── form.py
    └── list.py
```

### Barrel Export Pattern

In `jobs/detail/__init__.py`:
```python
"""
Job Detail Page Components

Provides both feature-domain and component-type access patterns.
"""

# Feature-domain exports (primary)
from .buttons import (
    button_save,
    button_cancel,
    button_edit,
    button_delete_job,
)
from .forms import (
    note_input_form,
    template_selection_form,
)
from .templates import (
    template_selector_list,
    template_search_input,
)
from .dialogs import (
    delete_confirmation_dialog,
    view_all_templates_dialog,
)

# Component-type grouped exports (secondary - for refactoring)
__all_buttons__ = [
    button_save,
    button_cancel,
    button_edit,
    button_delete_job
]
__all_forms__ = [note_input_form, template_selection_form]
__all_dialogs__ = [delete_confirmation_dialog, view_all_templates_dialog]

# Make everything available
__all__ = [
    # Buttons
    'button_save', 'button_cancel', 'button_edit', 'button_delete_job',
    # Forms
    'note_input_form', 'template_selection_form',
    # Templates
    'template_selector_list', 'template_search_input',
    # Dialogs
    'delete_confirmation_dialog', 'view_all_templates_dialog',
    # Grouped exports
    '__all_buttons__', '__all_forms__', '__all_dialogs__',
]
```

### Usage:
```python
# Domain-based import (most common)
from components.jobs.detail import button_save, template_selector_list

# Type-based refactoring (when needed)
from components.jobs.detail import __all_buttons__
for btn in __all_buttons__:
    apply_consistent_styling(btn)
```

---

## Solution 2: Component Catalog (Documentation Layer)

Create a `COMPONENTS.md` mapping file that provides both views:

```markdown
# Component Catalog

## By Type

### Buttons (15 total)
- `button_save` - jobs/detail/buttons.py:12 - Saves status changes
- `button_cancel` - jobs/detail/buttons.py:24 - Cancels edit mode
- `button_edit` - jobs/detail/buttons.py:36 - Enables status editing
- `button_template_selector` - jobs/detail/templates.py:48 - Quick template insert
- `button_template_insert` - jobs/detail/templates.py:60 - Inserts in dialog
- `button_dialog_close` - jobs/detail/dialogs.py:72 - Closes dialog

### Forms (8 total)
- `note_input_textarea` - jobs/detail/forms.py:15 - Note entry field
- `template_search_input` - jobs/detail/templates.py:27 - Template search
- `status_dropdown` - jobs/detail/forms.py:40 - Status selector

### Text Components (12 total)
- `job_title_heading` - jobs/detail/text.py:10 - Job title display
- `no_notes_placeholder` - jobs/detail/text.py:22 - Empty state text
- `template_name_text` - jobs/detail/templates.py:34 - Template name

## By Feature Domain

### Template System (18 components)
**Files:** `jobs/detail/templates.py`, `jobs/detail/dialogs.py`

#### Buttons (5)
- `button_template_selector` - Quick insertion from list
- `button_template_insert` - Insert in "View All" dialog
- `button_view_all` - Opens full template dialog
- `template_settings_tooltip` - Settings icon link

#### Forms/Inputs (3)
- `template_search_input` - Search templates by name/content
- `template_selector_list` - Scrollable template buttons
- `note_form_template_selection` - Full template section

#### Display (4)
- `template_name_text` - Template name display
- `template_content_text` - Template content preview
- `template_list_item` - Single template in dialog
- `view_all_templates_dialog` - Full dialog component

### Status Editing (6 components)
**Files:** `jobs/detail/buttons.py`, `jobs/detail/forms.py`

- `button_save` - Commits status change
- `button_cancel` - Cancels edit mode
- `button_edit` - Enables editing
- `status_dropdown` - Status selector
- `company_and_status` - Header with editable badge
- `job_information_card` - Main container

### Note Management (8 components)
**Files:** `jobs/detail/forms.py`, `jobs/notes.py`

- `note_input_textarea` - Note entry field
- `note_history_list` - Timeline of notes
- `note_history_no_notes_text` - Empty state
- `section_note_history` - History card
- `section_note_form` - Add note card
- `timeline` - Single note display
- `timeline_bullet` - Timeline marker
- `timeline_timestamp` - Note timestamp
```

### Auto-Generation Script

Create `scripts/generate_catalog.py`:
```python
import ast
import os
from pathlib import Path

def extract_component_info(file_path):
    """Parse Python file and extract component function information."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    components = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Extract function name, line number, docstring
            name = node.name
            line_no = node.lineno
            docstring = ast.get_docstring(node) or "No description"

            # Parse docstring for emoji and description
            lines = docstring.split('\n')
            emoji = lines[0].split()[0] if lines else ""
            desc = lines[0].replace(emoji, "").strip() if lines else ""

            components.append({
                'name': name,
                'file': str(file_path),
                'line': line_no,
                'emoji': emoji,
                'description': desc
            })

    return components

def generate_catalog(components_dir):
    """Generate COMPONENTS.md from all component files."""
    # Scan all .py files in components/
    # Extract component info
    # Group by type (prefix-based) and domain (directory-based)
    # Generate markdown
    pass

if __name__ == "__main__":
    generate_catalog("applog/components/")
```

Run after each major change: `python scripts/generate_catalog.py`

---

## Solution 3: Storybook / Interactive Component Browser

**Storybook** is the industry-standard tool for component catalogs in JavaScript/React. For Python/Reflex, you can create a similar system.

### What Storybook Provides:

1. **Visual Component Gallery**
   - See all components rendered in isolation
   - Interactive playground to test props/states
   - Searchable by name, type, or feature

2. **Live Documentation**
   - Auto-generated from docstrings and type hints
   - Shows component API (parameters, return types)
   - Includes usage examples

3. **Multiple Organization Views**
   - Sidebar tree organized by feature domain
   - Tag-based filtering by component type
   - Search across all metadata

4. **Testing Playground**
   - Adjust props in real-time
   - See component in different states
   - Test edge cases visually

### Reflex-Specific Implementation

Create `storybook.py` in your project:

```python
"""
Component Storybook - Interactive component catalog
Run: reflex run --env storybook
"""
import reflex as rx
from typing import List, Dict
from components.jobs import detail, card, form
from components.shared import buttons, inputs
from components.templates import manager

class StorybookState(rx.State):
    """State for component browser."""

    selected_component: str = ""
    search_query: str = ""
    filter_type: str = "all"  # all, button, form, dialog, etc.
    filter_domain: str = "all"  # all, jobs, templates, shared

    # Component registry
    components: List[Dict] = [
        {
            "name": "button_save",
            "module": "jobs.detail.buttons",
            "type": "button",
            "domain": "jobs/detail",
            "tags": ["status-editing", "interactive"],
            "description": "Saves status changes",
        },
        # ... more components
    ]

    @rx.var
    def filtered_components(self) -> List[Dict]:
        """Filter components based on search and filters."""
        result = self.components

        if self.search_query:
            result = [
                c for c in result
                if self.search_query.lower() in c["name"].lower()
                or self.search_query.lower() in c["description"].lower()
            ]

        if self.filter_type != "all":
            result = [c for c in result if c["type"] == self.filter_type]

        if self.filter_domain != "all":
            result = [c for c in result if c["domain"].startswith(self.filter_domain)]

        return result

def component_preview_card(component: Dict) -> rx.Component:
    """Render a component preview card."""
    return rx.card(
        rx.vstack(
            rx.heading(component["name"], size="4"),
            rx.badge(component["type"]),
            rx.text(component["description"], size="2"),
            rx.divider(),
            # Render actual component in isolation
            rx.box(
                # eval(f"{component['module']}.{component['name']}()")
                # ^ Dynamic component rendering
                padding="1em",
                border=f"1px solid {rx.color('gray', 6)}",
            ),
            spacing="2",
        ),
        width="300px",
    )

def storybook_page() -> rx.Component:
    """Main storybook interface."""
    return rx.container(
        rx.hstack(
            # Sidebar with filters
            rx.vstack(
                rx.heading("Component Browser", size="6"),
                rx.input(
                    placeholder="Search components...",
                    value=StorybookState.search_query,
                    on_change=StorybookState.set_search_query,
                ),
                rx.select(
                    ["all", "button", "form", "dialog", "input"],
                    value=StorybookState.filter_type,
                    on_change=StorybookState.set_filter_type,
                ),
                rx.select(
                    ["all", "jobs", "templates", "shared"],
                    value=StorybookState.filter_domain,
                    on_change=StorybookState.set_filter_domain,
                ),
                width="250px",
            ),

            # Component grid
            rx.box(
                rx.grid(
                    rx.foreach(
                        StorybookState.filtered_components,
                        component_preview_card,
                    ),
                    columns="3",
                    spacing="4",
                ),
                flex="1",
            ),

            spacing="4",
        ),
        padding="2em",
    )
```

### Benefits:
- **Dual Navigation**: Filter by type OR domain simultaneously
- **Visual Testing**: See components in isolation
- **Living Documentation**: Always up-to-date
- **Onboarding Tool**: New devs explore components visually

---

## Solution 4: IDE Features (Pragmatic Reality)

Most professional developers rely on IDE tooling:

### VSCode Symbol Search
- `Cmd+Shift+O` → Search all functions in current file
- `Cmd+T` → Search all functions across workspace
- Type `button` → See all button functions instantly

### PyCharm/IntelliJ
- `Cmd+O` → Go to symbol
- `Cmd+Shift+F` → Find in path with regex
- Structure view shows all functions grouped by file

### Tag-Based Search
Add structured tags to docstrings:

```python
def _button_save(state: rx.State):
    """
    💾 Saves status changes

    Tags: #button #status-editing #job-detail #interactive
    Category: buttons
    Domain: jobs/detail
    """
    pass
```

Then search: `#button` finds all buttons, `#status-editing` finds all status components.

---

## Solution 5: Hybrid Naming (Current Approach)

For **single-file components** (before splitting), use hybrid naming:

### Pattern:
```python
# Component type prefix for quick grouping
_button_save
_button_cancel
_button_edit
_button_dialog_close

# Feature-specific components with descriptive names
_button_template_selector
_button_template_insert

# Sub-feature grouping with common prefix
_template_selector_list
_template_search_input
_template_settings_tooltip

# Formatting dictionaries always prefixed
_formatting_button_section
_formatting_template_list
_formatting_dialog_content
```

### Why This Works:
- `_button_*` groups all buttons → Type-based access
- `_template_*` groups template components → Domain-based access
- Both accessible via IDE search
- Scales well up to ~100 components per file

### Add File Header Documentation:
```python
"""
Job Detail Page Components

Component Organization:

By Type:
  Buttons: _button_save, _button_cancel, _button_edit, _button_delete_job,
           _button_view_all, _button_template_selector, _button_template_insert,
           _button_dialog_close
  Inputs: _template_search_input, _note_input_textarea
  Text: _job_title, _template_name_text, _template_content_text,
        _no_notes_placeholder, _job_not_found_text
  Sections: _section_details_grid, _section_note_history, _section_note_form
  Dialogs: _delete_confirmation_dialog, _view_all_templates_dialog
  Formatting: _formatting_* (all styling dictionaries)

By Feature Domain:
  Status Editing:
    _button_save, _button_cancel, _button_edit, _status_dropdown,
    _company_and_status

  Template System:
    _button_template_selector, _button_template_insert, _button_view_all,
    _template_search_input, _template_selector_list, _template_settings_tooltip,
    _template_list_item, _view_all_templates_dialog, _note_form_template_selection

  Note Management:
    _note_input_textarea, _note_history_list, _section_note_history,
    _section_note_form, _add_note_section, _button_add_note

  Grid Details:
    _grid_location, _grid_applied_status, _grid_salary_conditional,
    _grid_url_conditional, _section_details_grid

  Dialogs:
    _delete_confirmation_dialog, _view_all_templates_dialog,
    _dialog_close_section, _button_dialog_close
"""
```

---

## When to Use Each Approach

### Single File (<100 components)
✅ **Hybrid naming + header documentation**
- Fast to implement
- IDE search works great
- No overhead

### Medium Project (100-500 components)
✅ **Directory structure + barrel exports**
- Feature folders for domains
- Component type files within folders
- `__init__.py` provides both access patterns

### Large Project (500+ components)
✅ **All of the above + Storybook**
- Directory structure
- Auto-generated catalog (COMPONENTS.md)
- Interactive component browser
- CI/CD integration for docs

---

## Production Reality Check

**What professional teams actually do:**

1. **Directory structure** for feature organization
2. **File names** for component type grouping
3. **IDE search** for day-to-day work (90% of lookups)
4. **Storybook/Catalog** for onboarding and visual testing
5. **Documentation** for architectural decisions

**The 80/20 rule:** Good directory structure + IDE search solves 80% of problems. The remaining 20% (onboarding, refactoring, auditing) benefits from catalogs and Storybook.

---

## Recommendation for This Project

### Current Phase (Refactoring in Progress):
✅ Keep hybrid naming (`_button_*`, `_template_*`)
✅ Add file header documentation (shown above)
✅ No additional tooling needed

### Next Phase (After File Splitting):
✅ Use directory structure:
```
components/jobs/detail/
├── buttons.py
├── forms.py
├── templates.py
└── __init__.py  # Barrel exports
```

### Future (If Team Grows):
✅ Add auto-generated COMPONENTS.md
✅ Consider Storybook-style browser

**Don't over-engineer early.** The hybrid approach is perfect for where you are now.