# **applog**

### An application logger tool to track job applications using a simple interface with filtering, status updates, and email notifications. Can be upgraded to scrape job listings and automate the workflow.

---

# **Implementation Status**

## 1. User Interface
   - [x] **Design & Layout**
     - [x] Modern, minimal interface in beige/white color palette with dark grey text
     - [x] Dark mode in dark brown/light brown with grey text (needs refinement)
     - [x] Main layout with search bar (fully functional)
     - [x] Job list/cards display with hover effects
     - [x] Total applications counter displayed on main page
   - [x] **Search & Filtering**
     - [x] Search field (main field, across the screen)
     - [x] Filter sidebar with dropdowns (company, status, location)
     - [ ] Add option to filter by location in the search bar
   - [x] **Forms & Input**
     - [x] Add job form (separate page at /add-job with all fields)
     - [x] Vertically expandable text fields for description and notes
     - [x] Job detail page with "View Details" navigation
     - [x] Status editing from job detail page (click "Edit" button next to status badge)
     - [x] Delete job from job detail page with confirmation dialog
     - [ ] Edit/delete buttons on job cards
     - [ ] Optional field to store apartment offer links (multiple links with '+ Add link' UI)
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

## 5. Future Services (v2+)
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

# **Lessons Learned**

## Reflex Var Handling in Templates

### Issue
**Reflex `Var` objects cannot be used with Python functions that contain conditional checks or type operations on the Var parameter itself.** Vars are reactive proxy objects, not plain values, and conditionals like `if isinstance(var, str)` or `if var` evaluate the Var object, not its runtime value.

### Symptoms
- Python functions return empty strings or default values
- Formatting functions fail silently in `rx.foreach` loops
- Dictionary `.get()` methods return None in templates

### Root Cause
When you pass a Reflex `Var` to a Python function that checks the parameter type or truthiness before converting to string, the check evaluates the Var wrapper object instead of the actual data. For example:
```python
def format_value(val):
    if not val:  # This checks the Var object, not its value!
        return ""
    return str(val).upper()
```

### Solutions

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

### Common Operations Affected
- **Date/time formatting** → Use `rx.moment()` or backend formatting
- **Currency/number formatting** → Backend formatting in `to_dict()`
- **String manipulation with validation** → Backend formatting or immediate string conversion
- **Conditional rendering** → Use `rx.cond()` instead of Python `if`
- **Dictionary field access in loops** → Use `dict["key"]` not `dict.get("key")`

### Key Takeaway
**When working with Reflex templates and reactive data, prefer backend formatting or Reflex-native components over Python utility functions.** This avoids Var serialization issues and improves maintainability.
