# **applog**

### An application logger tool. The purpose is to track my applications and display them using a simple interface that offers filtering, status updates, email notifications. Later can be upgraded to also scrape for job listings which can automate the whole flow.

# **Steps**

1. Create a simple UI
   - Modern, minimal interface in a white and beige color palette with dark grey text, and ideally a dark mode in dark brown, light brown and grey text.
   - Prepare fields. 
      - Search (main field, across the screen)
   - Filters 
     - Filter per company, per area, per status
2. Create the main software. The idea is to (initially) manually insert a link to a job offering to log it.
   - Logging system
     - Check for duplication (reject if already existing)
     - Capture created date
     - Automatically add "Applied" status (probably)
     - Store it to the database (more features will probably be added in this section)
   - Database
     - Simple LiteSQL database (probably, or MongoDB).
     - Store application data (extract keywords, company name, source website and more)
     - Later on I may choose to create a second database that will be holding company info.
3. Other services
      - Email notifications
        - Create email notifications after a certain period of time
        - Responding to the email may update the status of the job as necessary (if the service is running. if not, a check can be implemented to automatically run at next run).

# Flow

- Application is submitted with the company
- Job listing is manually inserted to the web interface
- Information is collected, scrubbed (if needed), serialized and stored

```
from dataclasses import dataclass, field
from datetime import datetime

class TestingSyntax:
    id: int
    timestamp: datetime = field(factory_default=datetime.now)


    def write_to_md() -> str:
        return "Testing code syntax inside the md file"

```

---

# **Project Architecture**

## Tech Stack
- **Frontend**: Reflex (pure Python framework that compiles to React)
- **Backend**: Python with SQLAlchemy ORM
- **Database**: SQLite (single-user, local storage)
- **Deployment**: Local only (runs on personal computer)

## MVP Priorities
For the initial version, focusing on:
1. **Core CRUD Operations** - Add, view, edit, and delete job applications - [job_service.py](applog/services/job_service.py)
2. **Search Functionality** - Full-text search across company, title, and description ✓
3. **Filtering System** - Filter by company, status, and location ✓
4. **Testing** - Ensure stable functionality and data integrity

## Features Deferred to v2
- Email notifications
- URL scraping/auto-extraction of job details
- Email response parsing
- Authentication (not needed for single-user)
- Company database (separate table)
- Web hosting

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
- `salary_range` - Salary range (optional)
- `notes` - Personal notes
- `created_at` - Record creation timestamp
- `updated_at` - Record update timestamp

## Implementation Phases

### Phase 1: Backend Foundation ✓
- SQLAlchemy models and database configuration
- CRUD operations with duplicate detection
- Search and filter logic
- Data validation

### Phase 2: Frontend with Reflex ✓ (~85% Complete)
- ✓ Reflex app setup with custom color palette (beige/white)
- ✓ Main layout with search bar (fully functional)
- ✓ Filter sidebar with dropdowns (company, status, location)
- ✓ Job list/cards display with hover effects
- ⚠ Add/edit job form (to be added)
- ⚠ Edit/delete buttons on job cards
- ⚠ Dark mode toggle (implemented but needs refinement)

### Phase 3: Testing & Documentation
- Unit tests for CRUD operations
- Search/filter functionality tests
- Usage documentation
