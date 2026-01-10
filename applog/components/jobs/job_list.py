import reflex as rx

from applog.components.jobs import job_card

_formatting_job_card_vstack = {
    "spacing": "4",
    "width": "100%",
}

_formatting_job_card_box = {
    "width": "100%"
}

def render_ui(state: rx.State) -> rx.Component:
    """
    📇 Renders the list of job application cards.
    Visual: Vertical stack of job cards (company name, title, status, dates).
            Each card is rendered by job_card.render_ui().
    """
    return rx.box(
        rx.vstack(
            rx.foreach(state.filtered_jobs, job_card.render_ui),

            **_formatting_job_card_vstack,
        ),

        **_formatting_job_card_box,
    )