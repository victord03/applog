"""AppLog - Job Application Tracker"""

import reflex as rx
from typing import List, Dict


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
        "notes": "Really interested in this position. Follow up next week.",
    },
    {
        "id": 2,
        "company_name": "StartupXYZ",
        "job_title": "Full Stack Engineer",
        "location": "Remote",
        "status": "Applied",
        "application_date": "2025-10-20",
        "salary_range": "$100k - $130k",
        "notes": "Reached out to hiring manager on LinkedIn.",
    },
    {
        "id": 3,
        "company_name": "Enterprise Solutions Inc",
        "job_title": "Backend Developer",
        "location": "New York, NY",
        "status": "Rejected",
        "application_date": "2025-09-28",
        "salary_range": "$110k - $140k",
        "notes": "They went with internal candidate.",
    },
    {
        "id": 4,
        "company_name": "Data Analytics Co",
        "job_title": "Data Engineer",
        "location": "Boston, MA",
        "status": "Screening",
        "application_date": "2025-10-18",
        "salary_range": "$105k - $135k",
        "notes": "Phone screen scheduled for next Tuesday.",
    },
]


class State(rx.State):
    """The app state."""

    # Search and filter state
    search_query: str = ""
    selected_company: str = "All Companies"
    selected_status: str = "All Statuses"
    selected_location: str = "All Locations"

    # Mock job data
    jobs: List[Dict] = MOCK_JOBS

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
                rx.text(f"📅 {job['application_date']}", size="2", color="#666"),
                spacing="4",
            ),
            rx.cond(
                job.get("salary_range"),
                rx.text(
                    f"💰 {job['salary_range']}", size="2", color="#666", weight="medium"
                ),
            ),
            rx.cond(
                job.get("notes"),
                rx.text(job["notes"], size="2", color="#777", font_style="italic"),
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


def index() -> rx.Component:
    """Main application page."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            # Header
            rx.heading("AppLog", size="8", margin_bottom="0.5em"),
            rx.text("Track your job applications", color="#666", margin_bottom="2em"),
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
app.add_page(index)
