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
   - [x] **Search & Filtering**
     - [x] Search field (main field, across the screen)
     - [x] Filter sidebar with dropdowns (company, status, location)
     - [ ] Add option to filter by location in the search bar
   - [ ] **Forms & Input**
     - [ ] Add/edit job form
     - [ ] Edit/delete buttons on job cards
     - [ ] Optional field to store apartment offer links (multiple links with '+ Add link' UI)

## 2. Core Application Logic

   ### Data Management
   - [x] **CRUD Operations** - [job_service.py](applog/services/job_service.py)
     - [x] Create job applications
     - [x] Read by ID and URL
     - [x] Update with partial or full field changes
     - [x] Delete job applications
   - [x] **Validation & Data Integrity**
     - [x] Field validation (empty dict, invalid field names)
     - [x] Atomic updates (all-or-nothing, no partial updates)
     - [x] Transaction rollback on failures
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

## 3. Database
   - [x] **Implementation**
     - [x] SQLite database (single-user, local storage)
     - [x] SQLAlchemy ORM models and configuration
   - [ ] **Schema Enhancements**
     - [ ] Convert salary_range field from string to tuple(int, int)
     - [ ] Extract and store keywords, company name, source website metadata
     - [ ] Optional: Create separate Company database table with relationships

## 4. Testing & Documentation
   - [x] **Unit Tests** (17+ tests with comprehensive coverage)
     - [x] Create: duplicate detection, validation, empty data, rollback handling
     - [x] Read: by ID and URL, valid/invalid cases, edge cases
     - [x] Update: field validation, partial updates, nonexistent IDs, rollback
     - [x] Delete: success/failure scenarios, rollback
   - [ ] **Integration Tests**
     - [ ] Search/filter functionality tests
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

---

# **Project Architecture**

## Tech Stack
- **Frontend**: Reflex (pure Python framework that compiles to React)
- **Backend**: Python with SQLAlchemy ORM
- **Database**: SQLite (single-user, local storage)
- **Testing**: pytest with 17+ comprehensive tests
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
- `salary_range` - Salary range (optional)
- `notes` - Personal notes
- `created_at` - Record creation timestamp
- `updated_at` - Record update timestamp

---

# **Application Flow**

- Application is submitted with the company
- Job listing is manually inserted to the web interface
- Information is collected, scrubbed (if needed), serialized and stored
