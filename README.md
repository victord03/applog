# **applog**

### An application logger tool to track job applications using a simple interface with filtering, status updates, and email notifications. Can be upgraded to scrape job listings and automate the workflow.

---

# **Implementation Status**

## 1. User Interface
   - [x] **Design & Layout**
     - [x] Modern, minimal interface in beige/white color palette with dark grey text
     - [x] Full dark mode support with theme-aware colors (light/dark modes fully functional)
     - [x] Main layout with search bar (fully functional)
     - [x] Job list/cards display with hover effects
     - [x] Total applications counter displayed on main page
     - [x] Sort jobs by latest/newest first on main screen (by application_date DESC)
   - [x] **Search & Filtering**
     - [x] Search field (main field, across the screen)
     - [x] Filter sidebar with dropdowns (company, status, location)
     - [x] Hide inactive job statuses (Rejected, Withdrawn, No Response) by default from main screen
     - [x] Display filtered count in applications counter (shows "X of Y applications")
     - [ ] Add option to filter by location in the search bar
     - [x] Location dropdown with "Other" option for zero-typing job creation (Phase 3 - ROADMAP.md ✅)
   - [x] **Forms & Input**
     - [x] Add job form (separate page at /add-job with all fields)
     - [x] Vertically expandable text fields for description and notes
     - [x] Job detail page with "View Details" navigation
     - [x] Status editing from job detail page (click "Edit" button next to status badge)
     - [x] Delete job from job detail page with confirmation dialog
     - [ ] Edit/delete buttons on job cards
     - [ ] Optional field to store apartment offer links (multiple links with '+ Add link' UI)
     - [ ] Edit job details functionality (Issue #3)
   - [x] **Note History & Timeline**
     - [x] Vertical timeline display showing timestamped notes
     - [x] Notes sorted in reverse chronological order (newest first)
     - [x] Timestamps formatted as DD/MM/YYYY HH:mm for readability
     - [x] "Add Note" form on job detail page
     - [x] Note count indicator on job cards
     - [x] Automatic timestamp capture for each note
   - [x] **Date & Value Formatting**
     - [x] Application dates displayed as DD/MM/YYYY on main page and detail page
     - [x] Note timestamps displayed as DD/MM/YYYY HH:mm
     - [x] Salary values formatted with K suffix (e.g., "120K" instead of "120000")
   - [x] **Note Templates**
     - [x] Templates Management page (`/templates` route)
     - [x] Create, edit, and delete reusable note templates
     - [x] Real-time search by template name or content
     - [x] Template selector in job detail page with search
     - [x] Hover tooltips showing full template content
     - [x] Click to insert template into note textarea (non-destructive)
     - [x] "View All Templates" dialog
     - [x] Auto-clear success messages after 3 seconds
     - [x] Settings icon link to Templates Management page
     - [ ] Handle note templates in job creation form (Issue #2)
       - Decision needed: Add template selector to creation form OR remove notes field from creation entirely

## 2. Core Application Logic

   ### Data Management
   - [x] **CRUD Operations** - [job_service.py](applog/services/job_service.py)
     - [x] Create job applications
     - [x] Read by ID and URL
     - [x] Update with partial or full field changes
     - [x] Delete job applications
     - [x] Add timestamped notes to existing applications
   - [x] **Validation & Data Integrity**
     - [x] Field validation (empty dict, invalid field names)
     - [x] Atomic updates (all-or-nothing, no partial updates)
     - [x] Transaction rollback on failures
     - [x] Notes field migrated to JSON with automatic timestamp capture
     - [ ] Explicitly track job_url field presence (not just rely on SQLAlchemy NOT NULL)

   ### Duplicate Prevention
   - [x] **Exact Duplicate Detection**
     - [x] Check for existing job_url (reject if already exists)
   - [ ] **Similar Job Detection**
     - [ ] Detect same job from different sources (LinkedIn, Indeed, company site)
     - [ ] Match criteria: company_name + job_title + location + different URL domain
     - [ ] Prompt user confirmation via UI layer before creating similar entry

   ### Search & Discovery
   - [x] **Search Functionality**
     - [x] Full-text search across company, title, and description
   - [x] **Filtering System**
     - [x] Filter by company, status, and location

   ### Tracking Features
   - [x] **Automatic Data Capture**
     - [x] Capture created date (created_at timestamp)
     - [x] Automatically assign "Applied" status on creation
     - [x] Track updated date (updated_at timestamp)
   - [ ] **Location-Based Tracking**
     - [ ] Track region of each job listing to align with apartment renting search

   ### Note Templates
   - [x] **Template CRUD Operations** - [template_service.py](applog/services/template_service.py)
     - [x] Create reusable note templates
     - [x] Read templates by ID
     - [x] Get all templates ordered by name
     - [x] Search templates by name or content (case-insensitive)
     - [x] Update existing templates
     - [x] Delete templates
   - [x] **Template Validation**
     - [x] Require name and content fields
     - [x] Field validation (empty dict, invalid field names)
     - [x] Transaction rollback on failures

## 3. Database
   - [x] **Implementation**
     - [x] SQLite database (single-user, local storage)
     - [x] SQLAlchemy ORM models and configuration
     - [x] Notes field as JSON column storing timestamped note entries
   - [ ] **Schema Enhancements**
     - [ ] Convert salary_range field from string to tuple(int, int) or separate min/max columns
     - [ ] Extract and store keywords, company name, source website metadata
     - [ ] Optional: Create separate Company database table with relationships

## 4. Testing & Documentation
   - [x] **Unit Tests** (49 tests with comprehensive coverage - all passing)
     - [x] **Job Service Tests** (31 tests)
       - [x] Create: duplicate detection, validation, empty data, rollback handling
       - [x] Read: by ID and URL, valid/invalid cases, edge cases
       - [x] Update: field validation, partial updates, nonexistent IDs, rollback
       - [x] Delete: success/failure scenarios, rollback
       - [x] Notes: add_note functionality, append to existing notes, edge cases
     - [x] **Template Service Tests** (18 tests)
       - [x] Create: validation, missing fields, empty data, rollback
       - [x] Read: by ID, get all templates, search by name/content
       - [x] Update: field validation, empty dict, nonexistent IDs
       - [x] Delete: success/failure scenarios
   - [ ] **Integration Tests**
     - [ ] Search/filter functionality tests
     - [ ] Form submission end-to-end tests
   - [ ] **Documentation**
     - [ ] Usage documentation

## 5. Code Quality & Refactoring
   - [x] **Component Organization** (✅ Complete - Branch: `refactor/component-extraction`)
     - [x] Create `applog/components/` directory structure
       - [x] `components/jobs/` - Job-related components
       - [x] `components/shared/` - Shared/reusable components
       - [x] `components/main/` - Main page components
       - [x] `components/templates/` - Template management components
     - [x] **Extract reusable UI components from `applog.py`** (✅ 100% complete - **App runs successfully!**)
       - [x] Job card component → `jobs/job_card.py` (with visual docstrings)
       - [x] Job detail page → `jobs/job_detail.py` (877 lines, ~50 functions, with visual docstrings)
       - [x] Add job form → `jobs/add_job.py` (with visual docstrings)
       - [x] Note timeline → `jobs/notes.py` (with visual docstrings)
       - [x] Filter sidebar → `shared/sidebar.py` (with visual docstrings)
       - [x] Status badge → `shared/status_badge.py` (with visual docstrings)
       - [x] Search bar → `shared/search_bar.py` (with visual docstrings)
       - [x] Formatters → `shared/formatters.py` (date formatting utilities)
       - [x] Job list wrapper → `jobs/job_list.py` (with visual docstrings)
       - [x] Main index page → `main/index_page.py` (with visual docstrings)
       - [x] Templates page → `templates/template_form.py` + `templates/template_list.py` (with visual docstrings)
     - [x] **Code Quality Improvements**
       - [x] Naming convention: `_button_*` prefix for all buttons (type-first organization)
       - [x] Naming convention: `_formatting_*` prefix for all styling dictionaries
       - [x] Visual docstrings added to all component functions (emoji + description + visual example)
       - [x] Component organization documented in LESSONS.md (type vs. domain strategies)
     - [x] **Module Integration** (✅ Complete)
       - [x] Configured `__init__.py` files for proper module exports
       - [x] Fixed import patterns (direct function calls vs. module.function access)
       - [x] Created page wrapper functions in `applog.py` for state injection
       - [x] Cleared stale bytecode cache and resolved import errors
     - [x] **Refactoring Complete!**
       - [x] All pages extracted into component modules
       - [x] Visual docstrings added to all functions
       - [x] Proper module exports via `__init__.py` files
       - [x] Consistent naming conventions throughout
       - [ ] Full integration testing of all features (recommended before merge)
       - [ ] Optional: Split large files into sub-modules if needed (only if files exceed 500 lines)

## 6. Future Services (v2+)
   - [ ] **Email Notifications**
     - [ ] Create email notifications after a certain period of time
     - [ ] Email response parsing to update job status automatically
     - [ ] Batch check on next run if service was offline
   - [ ] **URL Scraping**
     - [ ] Auto-extract job details from posting URLs
   - [ ] **Advanced Features**
     - [ ] Authentication (if multi-user support needed)
     - [ ] Web hosting deployment
     - [ ] Company database with historical tracking
   - [x] **Security**
     - [x] SQL injection protection (SQLAlchemy parameterized queries handle automatically)
     - [ ] Input validation for URL formats
     - [ ] Rate limiting (if deployed publicly)

---

# **Project Architecture**

## Tech Stack
- **Frontend**: Reflex (pure Python framework that compiles to React)
- **Backend**: Python with SQLAlchemy ORM
- **Database**: SQLite (single-user, local storage)
- **Testing**: pytest with 49 comprehensive tests (all passing)
- **Deployment**: Local development server only

## Database Schema

**JobApplication Table:**
- `id` - Primary key
- `company_name` - Company name (indexed)
- `job_title` - Position title
- `job_url` - Job posting URL (unique, for duplicate detection)
- `location` - Job location (indexed)
- `description` - Job description text
- `status` - Application status (indexed)
  - Options: Applied, Screening, Interview, Offer, Rejected, Accepted, Withdrawn, No Response
- `application_date` - Date applied
- `salary_range` - Salary range (optional, string format)
- `notes` - JSON array of timestamped note entries: `[{"timestamp": "ISO-8601", "note": "text"}, ...]`
- `created_at` - Record creation timestamp
- `updated_at` - Record update timestamp

**NoteTemplate Table:**
- `id` - Primary key
- `name` - Template name (indexed)
- `content` - Template text content
- `created_at` - Template creation timestamp
- `updated_at` - Template update timestamp

## Component Organization

### Current Approach: Hybrid Naming Convention

The project uses a **hybrid naming convention** that balances type-based and domain-based organization for components in single files:

**Type-First Prefixes** (for component kind):
- `_button_*` - All button components (e.g., `_button_save`, `_button_cancel`)
- `_formatting_*` - All styling dictionaries (e.g., `_formatting_card`, `_formatting_dialog`)
- `_grid_*` - Grid row components
- `_section_*` - Major page sections

**Domain-First Prefixes** (for features):
- `_template_*` - Template system components
- `_note_*` - Note management components
- `_job_*` - Job-related components

**Why This Works:**
- Enables both access patterns: "find all buttons" (`_button_*`) AND "find all template components" (`_template_*`)
- Works well with IDE search (Cmd+T / Cmd+Shift+O in VSCode)
- Scales up to ~100 components per file
- No tooling overhead required

**Example:**
```python
# Type-based grouping
_button_save          # Easy to find all buttons
_button_cancel
_button_template_insert

# Domain-based grouping
_template_selector_list   # Easy to find all template components
_template_search_input
_template_settings_tooltip
```

### File Organization (Current)

```
applog/
├── components/
│   ├── jobs/
│   │   ├── __init__.py        # Module exports
│   │   ├── job_card.py        # Job card display (~120 lines)
│   │   ├── job_detail.py      # Job detail page (~877 lines, 50+ functions)
│   │   ├── add_job.py         # Add job form (~340 lines)
│   │   ├── job_list.py        # Job list wrapper component (~30 lines)
│   │   └── notes.py           # Note timeline components
│   ├── shared/
│   │   ├── __init__.py        # Module exports
│   │   ├── sidebar.py         # Filter sidebar
│   │   ├── search_bar.py      # Search bar component
│   │   ├── status_badge.py    # Status badge component
│   │   └── formatters.py      # Date/currency formatting utilities
│   ├── main/
│   │   ├── __init__.py        # Module exports
│   │   └── index_page.py      # Main index page layout (~160 lines)
│   └── templates/
│       ├── __init__.py        # Module exports
│       ├── template_form.py   # Template form components (~220 lines)
│       └── template_list.py   # Template list display (~252 lines)
├── applog.py                  # Main app (State + page assembly, ~530 lines)
├── models/                    # Database models
│   ├── job_application.py
│   └── note_template.py
├── services/                  # Business logic layer
│   ├── job_service.py
│   └── template_service.py
└── database.py                # Database initialization
```

### Future: Directory Structure (100+ Components)

When the project grows beyond ~100 components, the plan is to reorganize into:

```
components/
├── jobs/
│   ├── detail/
│   │   ├── buttons.py      # All detail page buttons
│   │   ├── forms.py        # All form components
│   │   ├── dialogs.py      # Dialog components
│   │   └── __init__.py     # Barrel exports (dual access patterns)
│   ├── list/
│   │   ├── cards.py
│   │   └── filters.py
│   └── __init__.py
├── shared/
│   ├── buttons.py          # Shared button components
│   ├── inputs.py
│   └── status_badge.py
└── templates/
    ├── form.py
    └── list.py
```

**Barrel Export Pattern** (in `__init__.py`):
```python
# Feature-domain exports (primary)
from .buttons import button_save, button_cancel, button_edit

# Component-type grouped exports (for refactoring)
__all_buttons__ = [button_save, button_cancel, button_edit]
__all_forms__ = [...]
```

This provides:
- **Feature-domain imports**: `from components.jobs.detail import button_save`
- **Type-based refactoring**: `from components.jobs.detail import __all_buttons__`

### Design Philosophy

**The Trade-off**: You cannot optimize for both type-based AND domain-based access with a single hierarchy. The hybrid naming convention is a pragmatic compromise that works well for small-to-medium projects.

**Scaling Path**:
1. **< 100 components**: Hybrid naming in flat files ✅ (current)
2. **100-500 components**: Directory structure + barrel exports (planned)
3. **500+ components**: Add component catalog + Storybook (future)

**Key Principle**: Don't over-engineer early. The current approach is optimal for the project's scale.

**Full Details**: See `LESSONS_LEARNED.md` "Component Organization" section for the complete analysis of type vs. domain trade-offs, barrel export examples, and production best practices.

---

# **Application Flow**

## Current MVP Flow
1. **Add Job**: User navigates to `/add-job` and fills out the form with job details
2. **Data Storage**: Job application is saved to SQLite database with automatic timestamp and "Applied" status
3. **View Jobs**: Main page displays all applications with search/filter capabilities
   - Total applications counter displayed under "Add Job" button
   - "Templates" button for quick access to template management
   - Dates formatted as DD/MM/YYYY for easy reading
   - Salary values formatted with K suffix
   - Filter by company, status, or location
4. **View Details**: Click "View Details" on any job card to see full information
5. **Edit Status**: From job detail page, click "Edit" next to status badge to update application status
6. **Track Progress**: Add timestamped notes to track application progress (emails, interviews, etc.)
   - Use template selector to quickly insert common note text
   - Search templates by name or content
   - Hover over templates to preview full content
   - Click template to insert into note textarea (non-destructive)
   - "View All" button to see all templates in a dialog
   - Settings icon to manage templates
7. **Note History**: View vertical timeline of all notes with automatic timestamps
   - Notes displayed newest first (reverse chronological)
   - Timestamps formatted as DD/MM/YYYY HH:mm
8. **Delete Job**: From job detail page, click "Delete Job Application" button at bottom with confirmation dialog
9. **Manage Templates**: Navigate to `/templates` to create, edit, search, and delete note templates
   - Create reusable note templates with name and content
   - Real-time search across template names and content
   - Edit existing templates
   - Delete templates with confirmation
   - Success messages auto-clear after 3 seconds

## Pages
- `/` - Main dashboard with job list, search, filters, application counter, and Templates navigation button
- `/add-job` - Add new job application form (wired to database)
- `/job/[id]` - Job detail page with note history, status editing, add note with template selector, and delete job functionality
- `/templates` - Templates Management page for creating, editing, searching, and deleting note templates

---

# **Roadmap**

See [ROADMAP.md](ROADMAP.md) for detailed upcoming features and implementation plan.

**Phase 1: Complete ✅**
- ✅ Reset edit mode on page exit
- ✅ Smart cancel with confirmation dialog
- ✅ Auto-populate application date to today

**Phase 2: Complete ✅**
- ✅ Sort jobs by application date (newest first)
- ✅ Hide inactive job statuses by default
- ✅ Filter-aware application counter (shows "X of Y")
- ✅ Remove notes field from job creation (commented out for potential future re-add)

**Phase 3: Complete ✅**
- ✅ Location dropdown with "Other" option (zero-typing for 5 common locations)

**Coming Soon:**
- Full job editing capability (Phase 4)

