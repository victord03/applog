import reflex as rx

def _job_form_header(state: rx.State):
    """
    📋 Renders the form page header.
    Visual: [Add Job Application   ← Back to List button]
    """
    return rx.hstack(
        rx.heading("Add Job Application", size="7"),
        rx.spacer(),

        rx.button(
            "← Back to List",
            variant="soft",
            size="2",
            on_click=state.handle_cancel_job_creation,
        ),

        width="100%",
        align_items="center",
        margin_bottom="2em",
    )

def _required_field_company_name(state: rx.State):
    """
    🏢 Renders Company Name input field (required).
    Visual: Label "Company Name" + text input with placeholder
    """
    return rx.vstack(
            rx.text("Company Name", weight="bold", size="2"),
            rx.input(
                placeholder="e.g., Google, Microsoft, Startup Inc",
                value=state.form_company_name,
                on_change=state.set_form_company_name,
                width="100%",
                size="3",
            ),
            spacing="2",
            align_items="start",
            width="100%",
        )

def _required_field_job_title(state: rx.State):
    """
    💼 Renders Job Title input field (required).
    Visual: Label "Job Title" + text input with placeholder
    """
    return rx.vstack(
            rx.text("Job Title", weight="bold", size="2"),
            rx.input(
                placeholder="e.g., Senior Python Developer, Data Engineer",
                value=state.form_job_title,
                on_change=state.set_form_job_title,
                width="100%",
                size="3",
            ),
            spacing="2",
            align_items="start",
            width="100%",)

def _required_field_job_url(state: rx.State):
    """
    🔗 Renders Job URL input field (required).
    Visual: Label "Job URL" + URL-type input field
    """
    return rx.vstack(
            rx.text("Job URL", weight="bold", size="2"),
            rx.input(
                placeholder="https://...",
                value=state.form_job_url,
                on_change=state.set_form_job_url,
                width="100%",
                size="3",
                type="url",
            ),
            spacing="2",
            align_items="start",
            width="100%",)

def _section_required_fields(state: rx.State):
    """
    ✅ Renders the "Required Information" section.
    Visual: Section heading + company name, job title, and job URL fields + divider
    """
    return rx.vstack(

        rx.heading("Required Information", size="4", margin_bottom="1em"),

        _required_field_company_name(state),

        _required_field_job_title(state),

        _required_field_job_url(state),

        rx.divider(margin_top="1em", margin_bottom="1em"),

        spacing="4",
        align_items="start",
        width="100%",
    )

def _optional_field_location(state: rx.State):
    """
    📍 Renders Location dropdown field with "Other" option (optional).
    Visual: Label "Location" + select dropdown with preset locations + conditional text input for custom location
    """
    return rx.vstack(
        rx.text("Location", weight="bold", size="2"),
        rx.select(
            [
                "Geneva",
                "Lausanne",
                "Nyon",
                "Gland",
                "Bern",
                "Other",
            ],
            placeholder="Select a location...",
            value=rx.cond(
                state.form_location_is_other,
                "Other",
                state.form_location,
            ),
            on_change=state.handle_location_change,
            width="100%",
            size="3",
        ),
        # Conditional text input - only shown when "Other" is selected
        rx.cond(
            state.form_location_is_other,
            rx.input(
                placeholder="Enter custom location...",
                value=state.form_location,
                on_change=state.set_form_location,
                width="100%",
                size="3",
            ),
        ),
        spacing="2",
        align_items="start",
        width="100%",
    )

def _optional_field_status(state: rx.State):
    """
    🏷️ Renders Status dropdown field (optional).
    Visual: Label "Status" + select dropdown with predefined status options
    """
    return rx.vstack(

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
            value=state.form_status,
            on_change=state.set_form_status,
            width="100%",
            size="3",
        ),
        spacing="2",
        align_items="start",
        width="100%",
    )

def _optional_field_application_date(state: rx.State):
    """
    📅 Renders Application Date input field (optional).
    Visual: Label "Application Date" + date-type input field
    """
    return rx.vstack(
        rx.text("Application Date", weight="bold", size="2"),
        rx.input(
            value=state.form_application_date,
            on_change=state.set_form_application_date,
            width="100%",
            size="3",
            type="date",
        ),
        spacing="2",
        align_items="start",
        width="100%",
    )

def _optional_field_salary_range(state: rx.State):
    """
    💰 Renders Salary Range input field (optional).
    Visual: Label "Salary Range" + text input with placeholder (e.g., "$100k - $130k")
    """
    return rx.vstack(
        rx.text("Salary Range", weight="bold", size="2"),
        rx.input(
            placeholder="e.g., $100k - $130k",
            value=state.form_salary_range,
            on_change=state.set_form_salary_range,
            width="100%",
            size="3",
        ),
        spacing="2",
        align_items="start",
        width="100%",
    )

def _optional_field_description(state: rx.State):
    """
    📄 Renders Job Description textarea field (optional).
    Visual: Label "Job Description" + expandable text area for longer text input
    """
    return rx.vstack(
        rx.text("Job Description", weight="bold", size="2"),
        rx.text_area(
            placeholder="Paste or write the job description here...",
            value=state.form_description,
            on_change=state.set_form_description,
            width="100%",
            min_height="150px",
            resize="vertical",
        ),
        spacing="2",
        align_items="start",
        width="100%",
    )

def _optional_field_notes(state: rx.State):
    """
    📝 Renders Notes textarea field (optional).
    Visual: Label "Notes" + expandable text area for personal notes
    """
    return rx.vstack(
        rx.text("Notes", weight="bold", size="2"),
        rx.text_area(
            placeholder="Personal notes, follow-up reminders, contacts, etc...",
            value=state.form_notes,
            on_change=state.set_form_notes,
            width="100%",
            min_height="100px",
            resize="vertical",
        ),
        spacing="2",
        align_items="start",
        width="100%",
    )

def _optional_field_message_display(state: rx.State):
    """
    💬 Conditionally renders success/error message callout.
    Visual: Green callout for success, red callout for errors (only shown when message exists)
    """
    return rx.cond(
        state.form_message,
        rx.cond(
            state.form_message_type == "success",
            rx.callout(
                state.form_message,
                icon="info",
                color_scheme="green",
                size="2",
            ),
            rx.callout(
                state.form_message,
                icon="alert-triangle",
                color_scheme="red",
                size="2",
            ),
        ),
    )

def _form_actions(state: rx.State):
    """
    🎬 Renders form action buttons.
    Visual: [Cancel button]    [spacer]    [Save Job Application button]
    """
    return rx.hstack(

        rx.button(
            "Cancel",
            variant="soft",
            size="3",
            color_scheme="gray",
            on_click=state.handle_cancel_job_creation,
        ),
        rx.spacer(),
        rx.button(
            "Save Job Application",
            size="3",
            variant="solid",
            on_click=state.handle_submit,
        ),
        width="100%",
        margin_top="1.5em",
    )

def _section_optional_fields(state: rx.State):
    """
    📋 Renders the "Optional Information" section.
    Visual: Section heading + all optional fields (location, status, date, salary, description, notes, message display)
    """
    return rx.vstack(

        rx.heading("Optional Information", size="4", margin_bottom="1em"),

        _optional_field_location(state),

        _optional_field_status(state),

        _optional_field_application_date(state),

        _optional_field_salary_range(state),

        _optional_field_description(state),

        _optional_field_message_display(state),

        spacing="4",
        align_items="start",
        width="100%",
    )

def _job_form(state: rx.State):
    """
    📇 Renders the complete job application form card.
    Visual: Card container with required fields section + optional fields section + action buttons
    """
    return rx.card(

        rx.vstack(

            _section_required_fields(state),

            _section_optional_fields(state),

            _form_actions(state),

            spacing="4",
            width="100%",
        ),
        width="100%",
        padding="2em",
    )

def _cancel_confirmation_dialog(state: rx.State):
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Discard Job Application?"),
            rx.alert_dialog.description(
                "You have unsaved changes. Are you sure you want to leave without saving?"
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        "No, Stay",
                        variant="soft",
                        on_click=state.dismiss_cancel_dialog,
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Yes, Discard",
                        color_scheme="red",
                        on_click=state.confirm_cancel_job,
                    ),
                ),
                spacing="3",
            ),
        ),
        open=state.show_cancel_job_dialog,
    )

def render_ui(state: rx.State) -> rx.Component:
    """Add job application page."""
    return rx.fragment(
        rx.container(

            rx.color_mode.button(position="top-right"),

            rx.vstack(

                _job_form_header(state),

                _job_form(state),

                spacing="4",
                padding="2em",
                max_width="900px",
            ),
            padding="2em",
            min_height="100vh",
        ),
        _cancel_confirmation_dialog(state)
    )