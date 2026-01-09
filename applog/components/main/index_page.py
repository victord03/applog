import reflex as rx

from applog.components.shared import (
    search_bar,
    sidebar,
)

from applog.components.jobs import job_list

_formatting_main_area_with_filters_and_job_list = {
    "spacing": "6",
    "align_items": "start",
    "width": "100%",
    "margin_top": "2em"
}

_formatting_main_vstack = {
    "spacing": "4",
    "padding": "2em",
    "max_width": "1400px"
}

_formatting_main_general = {
    "padding": "2em",
    "min_height": "100vh"
}

_formatting_main_page_heading_stack = {
    "align_items": "start",
    "spacing": "2"
}

def _main_page_heading_text() -> rx.Component:
    return rx.text("Track your job applications", color=rx.color("gray", 11))

def _main_page_heading() -> rx.Component:
    return rx.vstack(

        rx.heading("AppLog", size="8", margin_bottom="0.5em"),

        _main_page_heading_text(),

        **_formatting_main_page_heading_stack,
    )

def _main_page_add_button() -> rx.Component:
    return rx.link(
        rx.button(
            "+ Add Job",
            size="3",
            variant="solid",
        ),
        href="/add-job",
    )

def _main_page_total_applications_display(state: rx.State) -> rx.Component:
    return rx.text(
        f"Applications: {state.total_jobs_count}",
        size="2",
        color=rx.color("gray", 10),
    )

_formatting_main_page_templates_button = {
    "size": "3",
    "variant": "soft"
}

def _main_page_templates_link() -> rx.Component:
    return rx.link(
        rx.button(
            "Templates",

            **_formatting_main_page_templates_button,
        ),

        href="/templates",
    )

_formatting_main_page_and_add_job_button = {
    "width": "100%",
    "align_items": "center",
    "margin_bottom": "2em"
}


def _render_heading(state: rx.State) -> rx.Component:
    return rx.hstack(
                _main_page_heading(),

                rx.spacer(),

                rx.vstack(
                    rx.hstack(

                        _main_page_templates_link(),

                        _main_page_add_button(),

                        spacing="3",
                    ),

                    _main_page_total_applications_display(state),

                    align_items="end",
                    spacing="2",
                ),

                **_formatting_main_page_and_add_job_button,
            )


def render_ui(state: rx.State) -> rx.Component:
    return rx.container(

        rx.color_mode.button(position="top-right"),

        rx.vstack(

            # Main page heading + Add Job button + Templates button
            _render_heading(state),

            # Search bar
            search_bar(state),

            # Main content area with filters and job list
            rx.hstack(
                sidebar.sb_filter(state),
                job_list.render_ui(state),

                **_formatting_main_area_with_filters_and_job_list,
            ),

            **_formatting_main_vstack,
        ),

        **_formatting_main_general,
    )