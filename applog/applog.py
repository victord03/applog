"""AppLog - Job Application Tracker"""

import reflex as rx

# Typing imports
from typing import List, Dict, Generator

# DB-related imports
from applog.database import SessionLocal, init_db
from applog.models.job_application import JobApplication

# Datetime
from datetime import datetime

# Single component-module imports
from applog.components.templates import template_list
from applog.components.shared import formatters
from applog.components.main import index_page

# Grouped component-module imports
from applog.services.job_service import (
    create_job,
    add_note,
    delete_job
)
from applog.services.template_service import (
    create_template,
    get_all_templates,
    update_template,
    delete_template,
)
from applog.components.jobs import (
    job_detail,
    add_job,
)

class State(rx.State):
    """The app state."""

    # STORED STATE VARIABLES

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
    form_location_is_other: bool = False  # Tracks if "Other" is selected in location dropdown
    form_description: str = ""
    form_status: str = "Applied"
    form_application_date: str
    form_salary_range: str = ""

    # Job detail page state
    selected_job_id: int = 0
    new_note_text: str = ""
    detail_status: str = ""  # For status update in detail page
    status_edit_mode: bool = False  # Toggle edit mode for status

    # Message state for user feedback
    form_message: str = ""
    form_message_type: str = ""  # "success" or "error"

    # Confirmation dialog for deletion operation
    show_delete_dialog: bool = False

    # Confirmation dialog for exiting job creation without save
    show_cancel_job_dialog: bool = False

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

    # COMPUTED PROPERTIES (@rx.var)
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
        if self.selected_status == "All Statuses":
            result = [job for job in result if job["status"] not in ["Rejected", "Withdrawn", "No Response"]]
        elif self.selected_status != "All Statuses":
            result = [job for job in result if job["status"] == self.selected_status]

        # Apply location filter
        if self.selected_location != "All Locations":
            result = [
                job for job in result if job["location"] == self.selected_location
            ]

        return result

    @rx.var
    def filtered_jobs_count(self) -> int:
        """Get total number of filtered job applications."""
        return len(self.filtered_jobs)

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
    def selected_job_application_date_formatted(self) -> str:
        """Get formatted application date for selected job."""

        if self.selected_job and self.selected_job.get("application_date"):

            return formatters.format_date(self.selected_job["application_date"])

        return "No date set"

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

    # EVENT HANDLERS
    def load_jobs_from_db(self) -> None:
        """Load all jobs from database and convert to dict format."""

        db = SessionLocal()

        try:
            job_records = db.query(JobApplication).order_by(JobApplication.application_date.desc()).all()
            self.jobs = [job.to_dict() for job in job_records]

        finally:
            db.close()

    def load_index_page(self) -> None:
        """Handler for index page load - loads jobs and clears messages."""
        self.load_jobs_from_db()
        self.form_message = ""  # Clear any form messages
        self.form_message_type = ""
        self.status_edit_mode = False

    def load_add_job_page(self) -> None:
        """Handler for add job page load - clears form messages."""
        self.clear_form()
        self.form_message = ""
        self.form_message_type = ""

    def load_job(self) -> Dict | None:
        """Load a job by ID from URL parameter."""

        # Load fresh data from database
        self.load_jobs_from_db()
        self.load_templates_from_db()

        # Clear template search query for fresh page load
        self.template_search_query = ""

        # Reset edit mode on page load
        self.status_edit_mode = False

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
            return None # Don't proceed

        # 1b. Validate location if "Other" is selected
        if self.form_location_is_other and not self.form_location:
            self.form_message = "Please enter a custom location or select a preset location"
            self.form_message_type = "error"
            return None

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

            # 7. Always closes the session
            db_session.close()

    def clear_form(self) -> None:
        """Reset all form fields to defaults."""
        self.form_company_name = ""
        self.form_job_title = ""
        self.form_job_url = ""
        self.form_location = ""
        self.form_location_is_other = False
        self.form_description = ""
        self.form_status = "Applied"
        self.form_application_date = datetime.today().strftime("%Y-%m-%d")
        self.form_salary_range = ""

    def handle_location_change(self, value: str) -> None:
        """Handle location dropdown selection change.

        If 'Other' is selected, enable custom text input mode.
        Otherwise, set location to selected preset value.
        """
        if value == "Other":
            self.form_location_is_other = True
            self.form_location = ""  # Clear location so user must enter custom value
        else:
            self.form_location_is_other = False
            self.form_location = value  # Set to selected preset location

    def handle_cancel_job_creation(self) -> None:
        """Handle cancel button click - show confirmation if form has data."""
        # Check if any form fields have been filled
        has_data = any([
            self.form_company_name,
            self.form_job_title,
            self.form_job_url,
            self.form_location,
            self.form_description,
            self.form_salary_range,
        ])

        if has_data:
            # Show confirmation dialog
            self.show_cancel_job_dialog = True
        else:
            # No data, just navigate away
            yield rx.redirect("/")

    def confirm_cancel_job(self):
        """Confirm cancellation - clear form and navigate away."""
        self.clear_form()
        self.show_cancel_job_dialog = False
        yield rx.redirect("/")

    def dismiss_cancel_dialog(self) -> None:
        """Dismiss the cancel confirmation dialog."""
        self.show_cancel_job_dialog = False

    def handle_add_note(self) -> Generator[Dict, None, None]:
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
                self.form_message = "Operation aborted"
                self.form_message_type = "error"
        except Exception as e:
            self.form_message = f"Error deleting job: {str(e)}"
            self.form_message_type = "error"
        finally:
            db.close()

    # TEMPLATE MANAGEMENT HANDLERS
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


def templates_page() -> rx.Component:
    """Note templates management page."""
    return template_list.render_ui(State)


def index() -> rx.Component:
    """Main application page."""
    return index_page.render_ui(State)


app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="brown",
    )
)

# Page wrappers to pass State to component functions
def add_job_page() -> rx.Component:
    """Wrapper for add job page component."""
    return add_job.render_ui(State)

def job_detail_page() -> rx.Component:
    """Wrapper for job detail page component."""
    return job_detail.render_ui(State)

app.add_page(index, on_load=State.load_index_page)
app.add_page(add_job_page, route="/add-job", on_load=State.load_add_job_page)
app.add_page(job_detail_page, route="/job/[job_id]", on_load=State.load_job)
app.add_page(templates_page, route="/templates", on_load=State.load_templates_page)

# Initialize database tables on app startup
init_db()
