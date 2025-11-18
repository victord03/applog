"""AppLog - Job Application Tracker"""

import reflex as rx
from typing import List, Dict
from applog.services.job_service import create_job, add_note, delete_job
from applog.services.template_service import (
    create_template,
    get_all_templates,
    update_template,
    delete_template,
)
from applog.database import SessionLocal, init_db
from applog.models.job_application import JobApplication
from applog.models.note_template import NoteTemplate


# Mock data for demonstration
MOCK_JOBS = [
    {
        "id": 1,
        "company_name": "Tech Corp",
        "job_title": "Senior Python Developer",
        "location": "San Francisco, CA",
        "status": "Interview",
        "application_date": "2025-10-15",
        "salary_range": "$120k - $150k",
        "job_url": "https://techcorp.com/jobs/123",
        "notes": [
            {
                "timestamp": "2025-10-15T09:00:00",
                "note": "Applied for position",
            },
            {
                "timestamp": "2025-10-18T14:30:00",
                "note": "Recruiter reached out for phone screen",
            },
            {
                "timestamp": "2025-10-20T10:00:00",
                "note": "Completed first technical interview - went well!",
            },
        ],
    },
    {
        "id": 2,
        "company_name": "StartupXYZ",
        "job_title": "Full Stack Engineer",
        "location": "Remote",
        "status": "Applied",
        "application_date": "2025-10-20",
        "salary_range": "$100k - $130k",
        "job_url": "https://startupxyz.com/careers/456",
        "notes": [
            {
                "timestamp": "2025-10-20T11:15:00",
                "note": "Submitted application through company website",
            },
            {
                "timestamp": "2025-10-21T16:45:00",
                "note": "Reached out to hiring manager on LinkedIn",
            },
        ],
    },
    {
        "id": 3,
        "company_name": "Enterprise Solutions Inc",
        "job_title": "Backend Developer",
        "location": "New York, NY",
        "status": "Rejected",
        "application_date": "2025-09-28",
        "salary_range": "$110k - $140k",
        "job_url": "https://enterprise.com/careers/789",
        "notes": [
            {
                "timestamp": "2025-09-28T08:00:00",
                "note": "Applied via Indeed",
            },
            {
                "timestamp": "2025-10-05T13:20:00",
                "note": "Received rejection email - they went with internal candidate",
            },
        ],
    },
    {
        "id": 4,
        "company_name": "Data Analytics Co",
        "job_title": "Data Engineer",
        "location": "Boston, MA",
        "status": "Screening",
        "application_date": "2025-10-18",
        "salary_range": "$105k - $135k",
        "job_url": "https://dataanalytics.com/jobs/101",
        "notes": [
            {
                "timestamp": "2025-10-18T15:30:00",
                "note": "Applied and got automated confirmation email",
            },
            {
                "timestamp": "2025-10-22T09:00:00",
                "note": "Phone screen scheduled for next Tuesday at 2pm",
            },
        ],
    },
]


class State(rx.State):
    """The app state."""

    # Search and filter state
    search_query: str = ""
    selected_company: str = "All Companies"
    selected_status: str = "All Statuses"
    selected_location: str = "All Locations"

    # Job data (loaded from database)
    jobs: List[Dict] = []

    # Add job form state
    form_company_name: str = ""
    form_job_title: str = ""
    form_job_url: str = ""
    form_location: str = ""
    form_description: str = ""
    form_status: str = "Applied"
    form_application_date: str = ""
    form_salary_range: str = ""
    form_notes: str = ""

    # Job detail page state
    selected_job_id: int = 0
    new_note_text: str = ""
    detail_status: str = ""  # For status update in detail page
    status_edit_mode: bool = False  # Toggle edit mode for status

    # Message state for user feedback
    form_message: str = ""
    form_message_type: str = ""  # "success" or "error"

    show_delete_dialog: bool = False

    # Template management state
    templates: List[Dict] = []
    template_search_query: str = ""
    selected_template_id: int = 0

    # Template form state
    form_template_name: str = ""
    form_template_content: str = ""
    template_edit_mode: bool = False
    show_templates_dialog: bool = False
    show_delete_template_dialog: bool = False

    @rx.var
    def total_jobs_count(self) -> int:
        """Get total number of job applications."""
        return len(self.jobs)

    @rx.var
    def filtered_jobs(self) -> List[Dict]:
        """Filter jobs based on search and filters."""
        result = self.jobs

        # Apply search filter
        if self.search_query:
            result = [
                job
                for job in result
                if self.search_query.lower() in job["company_name"].lower()
                or self.search_query.lower() in job["job_title"].lower()
            ]

        # Apply company filter
        if self.selected_company != "All Companies":
            result = [
                job for job in result if job["company_name"] == self.selected_company
            ]

        # Apply status filter
        if self.selected_status != "All Statuses":
            result = [job for job in result if job["status"] == self.selected_status]

        # Apply location filter
        if self.selected_location != "All Locations":
            result = [
                job for job in result if job["location"] == self.selected_location
            ]

        return result

    @rx.var
    def unique_companies(self) -> List[str]:
        """Get unique company names."""
        return ["All Companies"] + sorted(
            list(set(job["company_name"] for job in self.jobs))
        )

    @rx.var
    def unique_statuses(self) -> List[str]:
        """Get unique statuses."""
        return ["All Statuses"] + sorted(list(set(job["status"] for job in self.jobs)))

    @rx.var
    def unique_locations(self) -> List[str]:
        """Get unique locations."""
        return ["All Locations"] + sorted(
            list(set(job["location"] for job in self.jobs))
        )

    @rx.var
    def selected_job(self) -> Dict | None:
        """Get the currently selected job for detail view."""
        for job in self.jobs:
            if job.get("id") == self.selected_job_id:
                return job
        return None

    @rx.var
    def selected_job_notes(self) -> List[Dict]:
        """Get notes for the selected job with proper type annotation for foreach."""
        if self.selected_job and self.selected_job.get("notes"):
            # Return in reverse chronological order (newest first)
            return list(reversed(self.selected_job["notes"]))
        return []

    @rx.var
    def filtered_templates(self) -> List[Dict]:
        """Filter templates based on search query."""
        if not self.template_search_query:
            return self.templates

        query = self.template_search_query.lower()
        return [
            t
            for t in self.templates
            if query in t["name"].lower() or query in t["content"].lower()
        ]

    @rx.var
    def selected_template(self) -> Dict | None:
        """Get the currently selected template."""
        for template in self.templates:
            if template.get("id") == self.selected_template_id:
                return template
        return None

    def load_jobs_from_db(self):
        """Load all jobs from database and convert to dict format."""
        db = SessionLocal()
        try:
            job_records = db.query(JobApplication).all()
            self.jobs = [job.to_dict() for job in job_records]
        finally:
            db.close()

    def load_index_page(self):
        """Handler for index page load - loads jobs and clears messages."""
        self.load_jobs_from_db()
        self.form_message = ""  # Clear any form messages
        self.form_message_type = ""

    def load_add_job_page(self):
        """Handler for add job page load - clears form messages."""
        self.form_message = ""
        self.form_message_type = ""

    def load_job(self):
        """Load a job by ID from URL parameter."""
        # Load fresh data from database
        self.load_jobs_from_db()
        self.load_templates_from_db()
        # Clear template search query for fresh page load
        self.template_search_query = ""
        # Access the route parameter from router state
        job_id = self.router.page.params.get("job_id", "0")
        try:
            self.selected_job_id = int(job_id)
            # Load current status for editing
            if self.selected_job:
                self.detail_status = self.selected_job.get("status", "Applied")
        except (ValueError, TypeError):
            self.selected_job_id = 0

    def handle_submit(self):
        """Handle job form submission."""
        # 1. Validate required fields
        if not self.form_company_name or not self.form_job_url or not self.form_job_title:
            self.form_message = "Please fill in all required fields (Company, Title, URL)"
            self.form_message_type = "error"
            return  # Don't proceed

        # 2. Clear any previous messages
        self.form_message = ""
        self.form_message_type = ""

        # 3. Create database session
        db_session = SessionLocal()

        try:
            # 4. Attempt to create job
            result = create_job(
                session=db_session,
                job_data={
                    "company_name": self.form_company_name,
                    "job_title": self.form_job_title,
                    "job_url": self.form_job_url,
                    "location": self.form_location,
                    "description": self.form_description,
                    "salary_range": self.form_salary_range,
                    "notes": self.form_notes
                }
            )

            # 5. Success - set message and redirect
            self.form_message = f"Success! {self.form_job_title} at {self.form_company_name} has been saved."
            self.form_message_type = "success"
            self.clear_form()
            return rx.redirect("/")

        except ValueError as e:
            # 6. Error - show message, keep form data for user to fix
            self.form_message = f"Error: {str(e)}"
            self.form_message_type = "error"
            # Don't clear form or redirect - user needs to fix the issue

        finally:
            # 7. Always close the session
            db_session.close()

    def clear_form(self):
        """Reset all form fields to defaults."""
        self.form_company_name = ""
        self.form_job_title = ""
        self.form_job_url = ""
        self.form_location = ""
        self.form_description = ""
        self.form_status = "Applied"
        self.form_application_date = ""
        self.form_salary_range = ""
        self.form_notes = ""

    def handle_add_note(self):
        """Handle adding a note to the current job."""
        # Validate note text
        if not self.new_note_text or not self.new_note_text.strip():
            return  # Don't add empty notes

        db = SessionLocal()
        try:
            # Add note to database
            result = add_note(db, self.selected_job_id, self.new_note_text.strip())

            if result:
                # Clear the input
                self.new_note_text = ""
                # Clear template search to avoid any filtering issues
                self.template_search_query = ""
                # Reload jobs from database to get updated notes
                self.load_jobs_from_db()
                # Force state refresh by yielding
                yield
        except Exception as e:
            self.form_message = f"Error adding note: {str(e)}"
            self.form_message_type = "error"
        finally:
            db.close()

    def handle_status_update(self):
        """Handle status update for the current job."""
        from applog.services.job_service import update_job
        from applog.models.job_application import ApplicationStatus

        if not self.detail_status:
            return

        db = SessionLocal()
        try:
            # Convert status string to Enum
            status_enum = ApplicationStatus(self.detail_status)

            # Update job status
            result = update_job(db, self.selected_job_id, {"status": status_enum})

            if result:
                # Reload jobs from database
                self.load_jobs_from_db()
                # Exit edit mode
                self.status_edit_mode = False
        except Exception as e:
            self.form_message = f"Error updating status: {str(e)}"
            self.form_message_type = "error"
        finally:
            db.close()

    def handle_delete_job(self):

        db = SessionLocal()
        try:
            if delete_job(db, self.selected_job_id):
                # todo printing message ?
                # self.form_message = f"Success! {self.selected_job["job_title"]} at {self.selected_job["job_company"]} has been deleted."
                # self.form_message_type = "success"
                self.show_delete_dialog = False
                return rx.redirect("/")
            else:
                # todo form_message usage ?
                self.form_message = "Operation aborted"
                self.form_message_type = "error"
        except Exception as e:
            # todo form_message usage ?
            self.form_message = f"Error deleting job: {str(e)}"
            self.form_message_type = "error"
        finally:
            db.close()

    # Template management handlers
    def load_templates_from_db(self):
        """Load all templates from database."""
        db = SessionLocal()
        try:
            template_records = get_all_templates(db)
            self.templates = [t.to_dict() for t in template_records]
        finally:
            db.close()

    def load_templates_page(self):
        """Handler for templates page load."""
        self.load_templates_from_db()
        self.form_message = ""
        self.form_message_type = ""

    async def handle_template_submit(self):
        """Handle template form submission (create or update)."""
        import asyncio

        if not self.form_template_name or not self.form_template_content:
            self.form_message = "Please fill in both name and content"
            self.form_message_type = "error"
            return

        db = SessionLocal()
        try:
            if self.template_edit_mode and self.selected_template_id:
                # Update existing template
                result = update_template(
                    db,
                    self.selected_template_id,
                    {
                        "name": self.form_template_name,
                        "content": self.form_template_content,
                    },
                )
                if result:
                    self.form_message = "Template updated successfully!"
                    self.form_message_type = "success"
            else:
                # Create new template
                result = create_template(
                    db,
                    {
                        "name": self.form_template_name,
                        "content": self.form_template_content,
                    },
                )
                self.form_message = "Template created successfully!"
                self.form_message_type = "success"

            self.clear_template_form()
            self.load_templates_from_db()

            # Auto-clear success message after 3 seconds
            yield
            await asyncio.sleep(3)
            self.form_message = ""
            self.form_message_type = ""
        except ValueError as e:
            self.form_message = f"Error: {str(e)}"
            self.form_message_type = "error"
        finally:
            db.close()

    def handle_edit_template(self, template_id: int):
        """Load template data into form for editing."""
        for template in self.templates:
            if template["id"] == template_id:
                self.selected_template_id = template_id
                self.form_template_name = template["name"]
                self.form_template_content = template["content"]
                self.template_edit_mode = True
                break

    def handle_delete_template(self):
        """Delete the selected template."""
        db = SessionLocal()
        try:
            if delete_template(db, self.selected_template_id):
                self.form_message = "Template deleted successfully!"
                self.form_message_type = "success"
                self.show_delete_template_dialog = False
                self.load_templates_from_db()
            else:
                self.form_message = "Template not found"
                self.form_message_type = "error"
        except Exception as e:
            self.form_message = f"Error deleting template: {str(e)}"
            self.form_message_type = "error"
        finally:
            db.close()

    def handle_insert_template(self, template_id: int):
        """Insert selected template content into note textarea."""
        for template in self.templates:
            if template["id"] == template_id:
                # Insert at end of current text (or replace if empty)
                if self.new_note_text:
                    self.new_note_text += "\n" + template["content"]
                else:
                    self.new_note_text = template["content"]
                break

    def clear_template_form(self):
        """Clear template form fields."""
        self.form_template_name = ""
        self.form_template_content = ""
        self.template_edit_mode = False
        self.selected_template_id = 0


def format_date(iso_date_str) -> str:
    """Format ISO date string to DD/MM/YYYY. Works with both strings and Reflex Vars."""
    try:
        from datetime import datetime
        # Convert to string immediately - no conditionals on Var parameter
        str_date = str(iso_date_str)
        # Now check the string value
        if str_date in ("", "None", "null"):
            return ""
        dt = datetime.fromisoformat(str_date)
        return dt.strftime("%d/%m/%Y")
    except (ValueError, AttributeError, TypeError):
        return ""


def format_datetime(iso_datetime_str) -> str:
    """Format ISO datetime string to DD/MM/YYYY HH:mm. Works with both strings and Reflex Vars."""
    try:
        from datetime import datetime
        # Convert to string immediately - no conditionals on Var parameter
        str_datetime = str(iso_datetime_str)
        # Now check the string value
        if str_datetime in ("", "None", "null"):
            return ""
        dt = datetime.fromisoformat(str_datetime)
        return dt.strftime("%d/%m/%Y %H:%M")
    except (ValueError, AttributeError, TypeError):
        return ""


def status_badge(status: str) -> rx.Component:
    """Create a status badge with appropriate styling."""
    color_map = {
        "Applied": "blue",
        "Screening": "purple",
        "Interview": "yellow",
        "Offer": "green",
        "Accepted": "grass",
        "Rejected": "red",
        "Withdrawn": "gray",
        "No Response": "orange",
    }
    return rx.badge(status, color_scheme=color_map.get(status, "gray"))


def job_card(job: Dict) -> rx.Component:
    """Render a single job application card."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(job["company_name"], size="5"),
                status_badge(job["status"]),
                justify="between",
                width="100%",
            ),
            rx.text(job["job_title"], size="3", weight="medium", color="#555"),
            rx.hstack(
                rx.text(f"📍 {job['location']}", size="2", color="#666"),
                rx.text(f"📅 {format_date(job['application_date'])}", size="2", color="#666"),
                spacing="4",
            ),
            rx.cond(
                job.get("salary_range_formatted"),
                rx.text(
                    f"💰 {job['salary_range_formatted']}", size="2", color="#666", weight="medium"
                ),
            ),
            rx.cond(
                job.get("notes"),
                rx.text(
                    "📝 Has notes",
                    size="2",
                    color="#777",
                    font_style="italic",
                ),
            ),
            # View Details button
            rx.link(
                rx.button(
                    "View Details →",
                    size="2",
                    variant="soft",
                    width="100%",
                ),
                href=f"/job/{job['id']}",
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        padding="1.2em",
        border_radius="8px",
        border="1px solid #e0d5c7",
        background="white",
        _hover={"box_shadow": "0 4px 12px rgba(0,0,0,0.1)", "border_color": "#d4c5b3"},
        transition="all 0.2s ease",
        width="100%",
    )


def search_bar() -> rx.Component:
    """Search bar component."""
    return rx.input(
        placeholder="Search by company or job title...",
        value=State.search_query,
        on_change=State.set_search_query,
        width="100%",
        size="3",
    )


def filter_sidebar() -> rx.Component:
    """Filter sidebar component."""
    return rx.box(
        rx.vstack(
            rx.heading("Filters", size="4", margin_bottom="1em"),
            # Company filter
            rx.vstack(
                rx.text("Company", weight="bold", size="2"),
                rx.select(
                    State.unique_companies,
                    value=State.selected_company,
                    on_change=State.set_selected_company,
                    width="100%",
                ),
                spacing="2",
                align_items="start",
                width="100%",
            ),
            # Status filter
            rx.vstack(
                rx.text("Status", weight="bold", size="2"),
                rx.select(
                    State.unique_statuses,
                    value=State.selected_status,
                    on_change=State.set_selected_status,
                    width="100%",
                ),
                spacing="2",
                align_items="start",
                width="100%",
            ),
            # Location filter
            rx.vstack(
                rx.text("Location", weight="bold", size="2"),
                rx.select(
                    State.unique_locations,
                    value=State.selected_location,
                    on_change=State.set_selected_location,
                    width="100%",
                ),
                spacing="2",
                align_items="start",
                width="100%",
            ),
            spacing="4",
            align_items="start",
            width="100%",
        ),
        padding="1.5em",
        border_radius="8px",
        background="#f9f6f1",
        border="1px solid #e0d5c7",
        min_width="250px",
    )


def job_list() -> rx.Component:
    """Display list of job cards."""
    return rx.box(
        rx.vstack(
            rx.foreach(State.filtered_jobs, job_card),
            spacing="4",
            width="100%",
        ),
        width="100%",
    )


def add_job() -> rx.Component:
    """Add job application page."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Add Job Application", size="7"),
                rx.spacer(),
                rx.link(
                    rx.button(
                        "← Back to List",
                        variant="soft",
                        size="2",
                    ),
                    href="/",
                ),
                width="100%",
                align_items="center",
                margin_bottom="2em",
            ),
            # Form
            rx.card(
                rx.vstack(
                    # Required fields section
                    rx.heading("Required Information", size="4", margin_bottom="1em"),
                    # Company Name
                    rx.vstack(
                        rx.text("Company Name", weight="bold", size="2"),
                        rx.input(
                            placeholder="e.g., Google, Microsoft, Startup Inc",
                            value=State.form_company_name,
                            on_change=State.set_form_company_name,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    # Job Title
                    rx.vstack(
                        rx.text("Job Title", weight="bold", size="2"),
                        rx.input(
                            placeholder="e.g., Senior Python Developer, Data Engineer",
                            value=State.form_job_title,
                            on_change=State.set_form_job_title,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    # Job URL
                    rx.vstack(
                        rx.text("Job URL", weight="bold", size="2"),
                        rx.input(
                            placeholder="https://...",
                            value=State.form_job_url,
                            on_change=State.set_form_job_url,
                            width="100%",
                            size="3",
                            type="url",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    rx.divider(margin_top="1em", margin_bottom="1em"),
                    # Optional fields section
                    rx.heading("Optional Information", size="4", margin_bottom="1em"),
                    # Location
                    rx.vstack(
                        rx.text("Location", weight="bold", size="2"),
                        rx.input(
                            placeholder="e.g., San Francisco, CA or Remote",
                            value=State.form_location,
                            on_change=State.set_form_location,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    # Status
                    rx.vstack(
                        rx.text("Status", weight="bold", size="2"),
                        rx.select(
                            [
                                "Applied",
                                "Screening",
                                "Interview",
                                "Offer",
                                "Rejected",
                                "Accepted",
                                "Withdrawn",
                                "No Response",
                            ],
                            value=State.form_status,
                            on_change=State.set_form_status,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    # Application Date
                    rx.vstack(
                        rx.text("Application Date", weight="bold", size="2"),
                        rx.input(
                            value=State.form_application_date,
                            on_change=State.set_form_application_date,
                            width="100%",
                            size="3",
                            type="date",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    # Salary Range
                    rx.vstack(
                        rx.text("Salary Range", weight="bold", size="2"),
                        rx.input(
                            placeholder="e.g., $100k - $130k",
                            value=State.form_salary_range,
                            on_change=State.set_form_salary_range,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    # Description
                    rx.vstack(
                        rx.text("Job Description", weight="bold", size="2"),
                        rx.text_area(
                            placeholder="Paste or write the job description here...",
                            value=State.form_description,
                            on_change=State.set_form_description,
                            width="100%",
                            min_height="150px",
                            resize="vertical",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    # Notes
                    rx.vstack(
                        rx.text("Notes", weight="bold", size="2"),
                        rx.text_area(
                            placeholder="Personal notes, follow-up reminders, contacts, etc...",
                            value=State.form_notes,
                            on_change=State.set_form_notes,
                            width="100%",
                            min_height="100px",
                            resize="vertical",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    # Message display
                    rx.cond(
                        State.form_message,
                        rx.cond(
                            State.form_message_type == "success",
                            rx.callout(
                                State.form_message,
                                icon="info",
                                color_scheme="green",
                                size="2",
                            ),
                            rx.callout(
                                State.form_message,
                                icon="alert-triangle",
                                color_scheme="red",
                                size="2",
                            ),
                        ),
                    ),
                    # Form actions
                    rx.hstack(
                        rx.link(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                size="3",
                                color_scheme="gray",
                            ),
                            href="/",
                        ),
                        rx.spacer(),
                        rx.button(
                            "Save Job Application",
                            size="3",
                            variant="solid",
                            on_click=State.handle_submit,
                        ),
                        width="100%",
                        margin_top="1.5em",
                    ),
                    spacing="4",
                    width="100%",
                ),
                width="100%",
                padding="2em",
            ),
            spacing="4",
            padding="2em",
            max_width="800px",
        ),
        padding="2em",
        background="#faf8f5",
        min_height="100vh",
    )


def note_timeline_item(note: Dict) -> rx.Component:
    """Render a single note in the timeline."""
    from datetime import datetime

    # Format timestamp using rx.moment for proper Var handling
    return rx.box(
        rx.hstack(
            rx.box(
                rx.box(
                    width="12px",
                    height="12px",
                    border_radius="50%",
                    background="#8b4513",
                ),
                width="12px",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(
                    rx.moment(note["timestamp"], format="DD/MM/YYYY HH:mm"),
                    size="1",
                    color="#888",
                    weight="medium",
                ),
                rx.text(
                    note["note"],
                    size="2",
                    color="#333",
                ),
                spacing="1",
                align_items="start",
                flex="1",
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        padding_left="1em",
        border_left="2px solid #e0d5c7",
        padding_bottom="1.5em",
        margin_left="5px",
    )


def job_detail() -> rx.Component:
    """Job detail page with full information and note history."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Job Details", size="7"),
                rx.spacer(),
                rx.link(
                    rx.button(
                        "← Back to List",
                        variant="soft",
                        size="2",
                    ),
                    href="/",
                ),
                width="100%",
                align_items="center",
                margin_bottom="2em",
            ),
            # Job information card
            rx.cond(
                State.selected_job,
                rx.vstack(
                    rx.card(
                        rx.vstack(
                            # Company and status
                            rx.hstack(
                                rx.heading(
                                    State.selected_job["company_name"],
                                    size="6",
                                ),
                                rx.cond(
                                    State.status_edit_mode,
                                    rx.hstack(
                                        rx.select(
                                            [
                                                "Applied",
                                                "Screening",
                                                "Interview",
                                                "Offer",
                                                "Rejected",
                                                "Accepted",
                                                "Withdrawn",
                                                "No Response",
                                            ],
                                            value=State.detail_status,
                                            on_change=State.set_detail_status,
                                            size="2",
                                        ),
                                        rx.button(
                                            "Save",
                                            size="1",
                                            on_click=State.handle_status_update,
                                        ),
                                        rx.button(
                                            "Cancel",
                                            size="1",
                                            variant="soft",
                                            on_click=State.set_status_edit_mode(False),
                                        ),
                                        spacing="2",
                                    ),
                                    rx.hstack(
                                        status_badge(State.selected_job["status"]),
                                        rx.button(
                                            "Edit",
                                            size="1",
                                            variant="ghost",
                                            on_click=State.set_status_edit_mode(True),
                                        ),
                                        spacing="2",
                                    ),
                                ),
                                justify="between",
                                width="100%",
                            ),
                            # Job title
                            rx.heading(
                                State.selected_job["job_title"],
                                size="4",
                                color="#555",
                                weight="medium",
                            ),
                            rx.divider(margin_y="1em"),
                            # Details grid
                            rx.vstack(
                                rx.hstack(
                                    rx.text("📍 Location:", weight="bold", size="2"),
                                    rx.text(
                                        State.selected_job["location"],
                                        size="2",
                                        color="#666",
                                    ),
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.text("📅 Applied:", weight="bold", size="2"),
                                    rx.text(
                                        format_date(State.selected_job["application_date"]),
                                        size="2",
                                        color="#666",
                                    ),
                                    spacing="2",
                                ),
                                rx.cond(
                                    State.selected_job.get("salary_range_formatted"),
                                    rx.hstack(
                                        rx.text("💰 Salary:", weight="bold", size="2"),
                                        rx.text(
                                            State.selected_job["salary_range_formatted"],
                                            size="2",
                                            color="#666",
                                        ),
                                        spacing="2",
                                    ),
                                ),
                                rx.cond(
                                    State.selected_job.get("job_url"),
                                    rx.hstack(
                                        rx.text("🔗 URL:", weight="bold", size="2"),
                                        rx.link(
                                            State.selected_job["job_url"],
                                            href=State.selected_job["job_url"],
                                            size="2",
                                            color="#8b4513",
                                            is_external=True,
                                        ),
                                        spacing="2",
                                    ),
                                ),
                                spacing="3",
                                align_items="start",
                                width="100%",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        padding="2em",
                        width="100%",
                    ),
                    # Note history section
                    rx.card(
                        rx.vstack(
                            rx.heading("Note History", size="5", margin_bottom="1em"),
                            rx.cond(
                                State.selected_job_notes,
                                rx.vstack(
                                    rx.foreach(
                                        State.selected_job_notes,
                                        note_timeline_item,
                                    ),
                                    spacing="0",
                                    width="100%",
                                ),
                                rx.text(
                                    "No notes yet. Add your first note below.",
                                    size="2",
                                    color="#888",
                                    font_style="italic",
                                ),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        padding="2em",
                        width="100%",
                        margin_top="1em",
                    ),
                    # Add note form with template selector
                    rx.card(
                        rx.vstack(
                            rx.heading("Add Note", size="4", margin_bottom="1em"),
                            # Template selector section
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Quick Insert from Templates:", weight="bold", size="2"),
                                    rx.spacer(),
                                    rx.hstack(
                                        rx.button(
                                            "View All",
                                            size="1",
                                            variant="ghost",
                                            on_click=State.set_show_templates_dialog(True),
                                        ),
                                        rx.tooltip(
                                            rx.link(
                                                rx.icon_button(
                                                    rx.icon("settings"),
                                                    size="1",
                                                    variant="ghost",
                                                ),
                                                href="/templates",
                                            ),
                                            content="Manage Templates",
                                        ),
                                        spacing="2",
                                        align_items="center",
                                    ),
                                    width="100%",
                                    align_items="center",
                                ),
                                rx.cond(
                                    State.templates,
                                    rx.vstack(
                                        rx.input(
                                            placeholder="Search templates...",
                                            value=State.template_search_query,
                                            on_change=State.set_template_search_query,
                                            width="100%",
                                            size="2",
                                        ),
                                        rx.box(
                                            rx.vstack(
                                                rx.foreach(
                                                    State.filtered_templates,
                                                    lambda template: rx.tooltip(
                                                        rx.button(
                                                            template["name"],
                                                            size="2",
                                                            variant="soft",
                                                            on_click=lambda: State.handle_insert_template(template["id"]),
                                                            width="100%",
                                                        ),
                                                        content=template["content"],
                                                    ),
                                                ),
                                                spacing="2",
                                                width="100%",
                                            ),
                                            max_height="200px",
                                            overflow_y="auto",
                                            width="100%",
                                            padding="0.5em",
                                            border_radius="6px",
                                            background="#f9f6f1",
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    rx.text(
                                        "No templates available. Create templates in the Templates page.",
                                        size="2",
                                        color="#888",
                                        font_style="italic",
                                    ),
                                ),
                                spacing="2",
                                width="100%",
                                padding="1em",
                                border_radius="6px",
                                background="#f5f1ec",
                                margin_bottom="1em",
                            ),
                            # Note textarea
                            rx.text_area(
                                placeholder="Enter your note here (e.g., 'Recruiter called for phone screen', 'Sent thank you email')...",
                                value=State.new_note_text,
                                on_change=State.set_new_note_text,
                                width="100%",
                                min_height="100px",
                                resize="vertical",
                            ),
                            rx.hstack(
                                rx.spacer(),
                                rx.button(
                                    "Add Note",
                                    size="3",
                                    variant="solid",
                                    on_click=State.handle_add_note,
                                ),
                                width="100%",
                                margin_top="1em",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        padding="2em",
                        width="100%",
                        margin_top="1em",
                    ),
                    # Delete job button
                    rx.box(
                        rx.button(
                            "Delete Job Application",
                            color_scheme="red",
                            variant="soft",
                            size="2",
                            on_click=State.set_show_delete_dialog(True),
                        ),
                        margin_top="2em",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.text("Job not found.", size="4", color="#888"),
            ),
            spacing="4",
            padding="2em",
            max_width="900px",
        ),
        # Delete confirmation dialog
        rx.alert_dialog.root(
            rx.alert_dialog.content(
                rx.alert_dialog.title("Delete Job Application"),
                rx.alert_dialog.description("Are you sure? This cannot be undone."),
                rx.flex(
                    rx.alert_dialog.cancel(
                        rx.button("Cancel", variant="soft", on_click=State.set_show_delete_dialog(False)),
                    ),
                    rx.alert_dialog.action(
                        rx.button("Delete", color_scheme="red", on_click=State.handle_delete_job),
                    ),
                    spacing="3",
                ),
            ),
            open=State.show_delete_dialog,
        ),
        # View All Templates dialog
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("All Templates"),
                rx.dialog.description(
                    "Click on a template name to insert it into your note."
                ),
                rx.box(
                    rx.cond(
                        State.templates,
                        rx.vstack(
                            rx.foreach(
                                State.templates,
                                lambda template: rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.text(
                                                template["name"],
                                                weight="bold",
                                                size="3",
                                                flex="1",
                                            ),
                                            rx.button(
                                                "Insert",
                                                size="1",
                                                variant="soft",
                                                on_click=lambda: [
                                                    State.handle_insert_template(template["id"]),
                                                    State.set_show_templates_dialog(False),
                                                ],
                                            ),
                                            width="100%",
                                            justify="between",
                                            align_items="center",
                                        ),
                                        rx.text(
                                            template["content"],
                                            size="2",
                                            color="#666",
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    padding="1em",
                                    border_radius="6px",
                                    background="#f9f6f1",
                                    border="1px solid #e0d5c7",
                                    width="100%",
                                ),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.text(
                            "No templates available.",
                            size="2",
                            color="#888",
                        ),
                    ),
                    max_height="400px",
                    overflow_y="auto",
                    padding="1em",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Close",
                            variant="soft",
                            on_click=State.set_show_templates_dialog(False),
                        ),
                    ),
                    spacing="3",
                    margin_top="1em",
                    justify="end",
                ),
            ),
            open=State.show_templates_dialog,
        ),
        padding="2em",
        background="#faf8f5",
        min_height="100vh",
    )


def templates_page() -> rx.Component:
    """Note templates management page."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Note Templates", size="7"),
                rx.spacer(),
                rx.link(
                    rx.button(
                        "← Back to Jobs",
                        variant="soft",
                        size="2",
                    ),
                    href="/",
                ),
                width="100%",
                align_items="center",
                margin_bottom="2em",
            ),
            # Search bar
            rx.input(
                placeholder="Search templates by name or content...",
                value=State.template_search_query,
                on_change=State.set_template_search_query,
                width="100%",
                size="3",
                margin_bottom="1em",
            ),
            # Add/Edit template form
            rx.card(
                rx.vstack(
                    rx.heading(
                        rx.cond(
                            State.template_edit_mode,
                            "Edit Template",
                            "Add New Template",
                        ),
                        size="5",
                        margin_bottom="1em",
                    ),
                    rx.vstack(
                        rx.text("Template Name", weight="bold", size="2"),
                        rx.input(
                            placeholder="e.g., Cover Letter Sent, Phone Screen Completed",
                            value=State.form_template_name,
                            on_change=State.set_form_template_name,
                            width="100%",
                            size="3",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Template Content", weight="bold", size="2"),
                        rx.text_area(
                            placeholder="The note text that will be inserted...",
                            value=State.form_template_content,
                            on_change=State.set_form_template_content,
                            width="100%",
                            min_height="100px",
                            resize="vertical",
                        ),
                        spacing="2",
                        align_items="start",
                        width="100%",
                    ),
                    # Message display
                    rx.cond(
                        State.form_message,
                        rx.cond(
                            State.form_message_type == "success",
                            rx.callout(
                                State.form_message,
                                icon="info",
                                color_scheme="green",
                                size="2",
                            ),
                            rx.callout(
                                State.form_message,
                                icon="alert-triangle",
                                color_scheme="red",
                                size="2",
                            ),
                        ),
                    ),
                    # Form actions
                    rx.hstack(
                        rx.cond(
                            State.template_edit_mode,
                            rx.button(
                                "Cancel",
                                variant="soft",
                                size="3",
                                on_click=State.clear_template_form,
                            ),
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.cond(
                                State.template_edit_mode,
                                "Update Template",
                                "Add Template",
                            ),
                            size="3",
                            variant="solid",
                            on_click=State.handle_template_submit,
                        ),
                        width="100%",
                        margin_top="1em",
                    ),
                    spacing="4",
                    width="100%",
                ),
                padding="2em",
                width="100%",
            ),
            # Templates list
            rx.card(
                rx.vstack(
                    rx.heading("Your Templates", size="5", margin_bottom="1em"),
                    rx.cond(
                        State.filtered_templates,
                        rx.vstack(
                            rx.foreach(
                                State.filtered_templates,
                                lambda template: rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.heading(
                                                template["name"], size="4", flex="1"
                                            ),
                                            rx.hstack(
                                                rx.button(
                                                    "Edit",
                                                    size="1",
                                                    variant="soft",
                                                    on_click=lambda: State.handle_edit_template(
                                                        template["id"]
                                                    ),
                                                ),
                                                rx.button(
                                                    "Delete",
                                                    size="1",
                                                    variant="soft",
                                                    color_scheme="red",
                                                    on_click=lambda: [
                                                        State.set_selected_template_id(
                                                            template["id"]
                                                        ),
                                                        State.set_show_delete_template_dialog(
                                                            True
                                                        ),
                                                    ],
                                                ),
                                                spacing="2",
                                            ),
                                            justify="between",
                                            width="100%",
                                        ),
                                        rx.text(
                                            template["content"],
                                            size="2",
                                            color="#666",
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    padding="1em",
                                    border_radius="6px",
                                    background="#f9f6f1",
                                    border="1px solid #e0d5c7",
                                    width="100%",
                                ),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.text(
                            "No templates found. Add one above!",
                            size="2",
                            color="#888",
                            font_style="italic",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                padding="2em",
                width="100%",
                margin_top="1em",
            ),
            spacing="4",
            padding="2em",
            max_width="900px",
        ),
        # Delete confirmation dialog
        rx.alert_dialog.root(
            rx.alert_dialog.content(
                rx.alert_dialog.title("Delete Template"),
                rx.alert_dialog.description(
                    "Are you sure? This cannot be undone."
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        rx.button(
                            "Cancel",
                            variant="soft",
                            on_click=State.set_show_delete_template_dialog(False),
                        ),
                    ),
                    rx.alert_dialog.action(
                        rx.button(
                            "Delete",
                            color_scheme="red",
                            on_click=State.handle_delete_template,
                        ),
                    ),
                    spacing="3",
                ),
            ),
            open=State.show_delete_template_dialog,
        ),
        padding="2em",
        background="#faf8f5",
        min_height="100vh",
    )


def index() -> rx.Component:
    """Main application page."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            # Header with Add Job button
            rx.hstack(
                rx.vstack(
                    rx.heading("AppLog", size="8", margin_bottom="0.5em"),
                    rx.text("Track your job applications", color="#666"),
                    align_items="start",
                    spacing="2",
                ),
                rx.spacer(),
                rx.vstack(
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
                    rx.text(
                        f"Applications: {State.total_jobs_count}",
                        size="2",
                        color="#888",
                    ),
                    align_items="end",
                    spacing="2",
                ),
                width="100%",
                align_items="center",
                margin_bottom="2em",
            ),
            # Search bar
            search_bar(),
            # Main content area with filters and job list
            rx.hstack(
                filter_sidebar(),
                job_list(),
                spacing="6",
                align_items="start",
                width="100%",
                margin_top="2em",
            ),
            spacing="4",
            padding="2em",
            max_width="1400px",
        ),
        padding="2em",
        background="#faf8f5",
        min_height="100vh",
    )


app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="brown",
    )
)
app.add_page(index, on_load=State.load_index_page)
app.add_page(add_job, route="/add-job", on_load=State.load_add_job_page)
app.add_page(job_detail, route="/job/[job_id]", on_load=State.load_job)
app.add_page(templates_page, route="/templates", on_load=State.load_templates_page)

# Initialize database tables on app startup
init_db()
