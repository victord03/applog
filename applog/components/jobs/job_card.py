import reflex as rx
from typing import Dict

from applog.components.shared import (
    status_badge,
    formatters
)

def _job_card_heading(job: Dict) -> rx.Component:
    """
    🏢 Renders the card header with company name and status badge.
    Visual: [Company Name   Status Badge]
    """
    return rx.hstack(
                rx.heading(job["company_name"], size="5"),
                status_badge(job["status"]),
                justify="between",
                width="100%",
    )

def _job_card_title(job: Dict) -> rx.Component:
    """
    💼 Renders the job title.
    Visual: Medium-weight gray text (e.g., "Senior Python Developer")
    """
    return rx.text(job["job_title"], size="3", weight="medium", color=rx.color("gray", 11))

def _job_card_metadata(job: Dict) -> rx.Component:
    """
    📍📅 Renders location and application date side by side.
    Visual: [📍 San Francisco, CA    📅 25/12/2025]
    """
    return rx.hstack(
        rx.text(f"📍 {job['location']}", size="2", color=rx.color("gray", 11)),
        rx.text(f"📅 {formatters.format_date(job['application_date'])}", size="2", color=rx.color("gray", 11)),
        spacing="4",
    )

def _job_card_salary(job: Dict) -> rx.Component:
    """
    💰 Conditionally renders salary range if available.
    Visual: "💰 120K - 150K" (only displayed if salary data exists)
    """
    return rx.cond(
        job.get("salary_range_formatted"),
        rx.text(
            f"💰 {job['salary_range_formatted']}", size="2", color=rx.color("gray", 11), weight="medium"
        ),
    )

def _job_card_notes(job: Dict) -> rx.Component:
    """
    📝 Conditionally renders notes indicator if job has notes.
    Visual: "📝 Has notes" in italic gray text (only shown if notes exist)
    """
    return rx.cond(
                job.get("notes"),
                rx.text(
                    "📝 Has notes",
                    size="2",
                    color=rx.color("gray", 10),
                    font_style="italic",
                ),
            )

def _view_details_button(job: Dict):
    """
    🔗 Renders the "View Details" navigation button.
    Visual: Soft-variant button with arrow (→) linking to job detail page
    """
    return rx.link(
        rx.button(
            "View Details →",
            size="2",
            variant="soft",
            width="100%",
        ),
        href=f"/job/{job['id']}",
    )

_formatting_job_card = {
    "padding": "1.2em",
    "border_radius": "8px",
    "border": f"1px solid {rx.color('gray', 6)}",
    "_hover": {"box_shadow": "0 4px 12px rgba(0,0,0,0.15)"},
    "transition": "all 0.2s ease",
    "width": "100%"
}

_vstack_layout = {
    "spacing": "3",
    "align_items": "start",
    "width": "100%"
}

def render_ui(job: Dict) -> rx.Component:
    """
    🎴 Renders a complete job application card.
    Visual: Bordered box with hover effect containing:
            - Company name + status badge (header)
            - Job title
            - Location + application date
            - Salary (if available)
            - Notes indicator (if notes exist)
            - View Details button
    """
    return rx.box(
        rx.vstack(

            _job_card_heading(job),

            _job_card_title(job),

            _job_card_metadata(job),

            _job_card_salary(job),

            _job_card_notes(job),

            _view_details_button(job),

            **_vstack_layout
        ),

        **_formatting_job_card
    )