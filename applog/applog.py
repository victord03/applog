"""AppLog - Job Application Tracker"""

import reflex as rx
from typing import List, Dict, Generator
from applog.services.job_service import create_job, add_note, delete_job
from applog.services.template_service import (
    create_template,
    get_all_templates,
    update_template,
    delete_template,
)
from applog.database import SessionLocal, init_db
from applog.models.job_application import JobApplication

from applog.components.jobs import (
    job_card,
    job_detail,
    add_job,
    job_list
)

from applog.components.shared import (
    formatters,
    search_bar,
    status_badge,
    sidebar
)

from applog.components.main import index_page


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

    # Confirmation dialog for deletion operation
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

    def load_jobs_from_db(self) -> None:
        """Load all jobs from database and convert to dict format."""

        db = SessionLocal()

        try:
            job_records = db.query(JobApplication).all()
            self.jobs = [job.to_dict() for job in job_records]

        finally:
            db.close()

    def load_index_page(self) -> None:
        """Handler for index page load - loads jobs and clears messages."""
        self.load_jobs_from_db()
        self.form_message = ""  # Clear any form messages
        self.form_message_type = ""

    def load_add_job_page(self) -> None:
        """Handler for add job page load - clears form messages."""
        self.form_message = ""
        self.form_message_type = ""

    def load_job(self) -> Dict | None:
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

    def handle_submit(self) -> None:
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

    def clear_form(self) -> None:
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
                                            color=rx.color("gray", 11),
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    padding="1em",
                                    border_radius="6px",
                                    bg=rx.color("gray", 2),
                                    border=f"1px solid {rx.color('gray', 6)}",
                                    width="100%",
                                ),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.text(
                            "No templates found. Add one above!",
                            size="2",
                            color=rx.color("gray", 10),
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
        min_height="100vh",
    )


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
    return add_job.form(State)

def job_detail_page() -> rx.Component:
    """Wrapper for job detail page component."""
    return job_detail.render_ui(State)

app.add_page(index, on_load=State.load_index_page)
app.add_page(add_job_page, route="/add-job", on_load=State.load_add_job_page)
app.add_page(job_detail_page, route="/job/[job_id]", on_load=State.load_job)
app.add_page(templates_page, route="/templates", on_load=State.load_templates_page)

# Initialize database tables on app startup
init_db()
