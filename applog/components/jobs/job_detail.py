import reflex as rx

from applog.components.shared import (
    status_badge
)

from applog.components.jobs.notes import timeline

def _page_heading() -> rx.Component:
    """
    📋 Renders the job detail page header.
    Visual: [Job Details                    ← Back to List button]
    """
    return rx.hstack(
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
    )

def _button_save(state: rx.State) -> rx.Component:
    """
    💾 Renders Save button for status editing.
    Visual: Small "Save" button that commits status changes
    """
    return rx.button(
        "Save",
        size="1",
        on_click=state.handle_status_update,
    )

def _button_cancel(state: rx.State) -> rx.Component:
    """
    ❌ Renders Cancel button for status editing.
    Visual: Soft-variant "Cancel" button that exits edit mode
    """
    return rx.button(
        "Cancel",
        size="1",
        variant="soft",
        on_click=state.set_status_edit_mode(False),
    )

def _button_edit(state: rx.State) -> rx.Component:
    """
    ✏️ Renders Edit button to enable status editing.
    Visual: Ghost-variant "Edit" button next to status badge
    """
    return rx.button(
        "Edit",
        size="1",
        variant="ghost",
        on_click=state.set_status_edit_mode(True),
    )

def _status_dropdown(state: rx.State) -> rx.Component:
    """
    🏷️ Renders status dropdown for editing.
    Visual: Select dropdown with all available status options
    """
    return rx.select(
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
        value=state.detail_status,
        on_change=state.set_detail_status,
        size="2",
    )

def _company_and_status(state: rx.State) -> rx.Component:
    """
    🏢🏷️ Renders company name with editable status badge.
    Visual: [Company Name        Status Badge + Edit] or [Company Name        Dropdown + Save/Cancel]
    Structure: Conditionally shows either view mode (badge + edit button) or edit mode (dropdown + save/cancel)
    """
    return rx.hstack(

        rx.heading(

            state.selected_job["company_name"],
            size="6",
        ),

        rx.cond(
            state.status_edit_mode,

            rx.hstack(

                _status_dropdown(state),

                _button_save(state),

                _button_cancel(state),

                spacing="2",
            ),

            rx.hstack(
                status_badge(state.selected_job["status"]),

                _button_edit(state),

                spacing="2",
            ),
        ),
        justify="between",
        width="100%",
    )

def _job_title(state: rx.State) -> rx.Component:
    """
    💼 Renders the job title heading.
    Visual: Medium-sized gray heading (e.g., "Senior Python Developer")
    """
    return rx.heading(
        state.selected_job["job_title"],
        size="4",
        color=rx.color("gray", 11),
        weight="medium",
    )

def _grid_location(state: rx.State) -> rx.Component:
    """
    📍 Renders location detail row.
    Visual: "📍 Location: San Francisco, CA"
    """
    return rx.hstack(
        rx.text("📍 Location:", weight="bold", size="2"),

        rx.text(
            state.selected_job["location"],
            size="2",
            color=rx.color("gray", 11),
        ),
        spacing="2",
    )

def _grid_applied_status(state: rx.State) -> rx.Component:
    """
    📅 Renders application date detail row.
    Visual: "📅 Applied: 25/12/2025"
    """
    return rx.hstack(
        rx.text("📅 Applied:", weight="bold", size="2"),

        rx.text(
            state.selected_job_application_date_formatted,
            size="2",
            weight="medium",
        ),
        spacing="2",
    )

def _grid_salary_conditional(state: rx.State) -> rx.Component:
    """
    💰 Conditionally renders salary detail row if available.
    Visual: "💰 Salary: 120K - 150K" (only shown if salary data exists)
    """
    return rx.cond(
        state.selected_job.get("salary_range_formatted"),

        rx.hstack(

            rx.text("💰 Salary:", weight="bold", size="2"),

            rx.text(
                state.selected_job["salary_range_formatted"],
                size="2",
                color=rx.color("gray", 11),
            ),
            spacing="2",
        ),
    )

def _grid_url_conditional(state: rx.State) -> rx.Component:
    """
    🔗 Conditionally renders job URL detail row if available.
    Visual: "🔗 URL: [clickable link]" (only shown if URL exists)
    """
    return rx.cond(
        state.selected_job.get("job_url"),
        rx.hstack(
            rx.text("🔗 URL:", weight="bold", size="2"),
            rx.link(
                state.selected_job["job_url"],
                href=state.selected_job["job_url"],
                size="2",
                color=rx.color("brown", 11),
                is_external=True,
            ),
            spacing="2",
        ),
    )

_formatting_details_grid = {
    "spacing": "3",
    "align_items": "start",
    "width": "100%",
}

def _section_details_grid(state: rx.State):
    """
    📊 Renders the job details grid section.
    Visual: Vertical stack of detail rows (location, date, salary, URL)
    """
    return rx.vstack(

        _grid_location(state),

        _grid_applied_status(state),

        _grid_salary_conditional(state),

        _grid_url_conditional(state),

        **_formatting_details_grid
    )

def _note_history_no_notes_text():
    """
    📝 Renders placeholder text when no notes exist.
    Visual: Italic gray text: "No notes yet. Add your first note below."
    """
    return rx.text(
        "No notes yet. Add your first note below.",
        size="2",
        color=rx.color("gray", 10),
        font_style="italic",
    )

def _note_history_list(state: rx.State):
    """
    📜 Renders the list of notes using timeline components.
    Visual: Vertical stack of timeline items (newest first)
    """
    return rx.vstack(
        rx.foreach(
            state.selected_job_notes,
            timeline,
        ),
        spacing="0",
        width="100%",
    )

_formatting_note_history_conditional = {
    "spacing": "3",
    "align_items": "start",
}

_formatting_note_section_history = {
    "padding": "2em",
    "width": "100%",
    "margin_top": "1em",
}

def _section_note_history(state: rx.State):
    """
    🗓️ Renders the note history section card.
    Visual: Card with "Note History" heading + timeline of notes or placeholder text
    Structure: Conditionally shows either note list or "no notes" message
    """
    return rx.card(

        rx.vstack(

            rx.heading("Note History", size="5", margin_bottom="1em"),

            rx.cond(

                # If this isn't empty...
                state.selected_job_notes,

                # Execute this
                _note_history_list(state),

                # Otherwise this
                _note_history_no_notes_text(),
            ),

            **_formatting_note_history_conditional
        ),

        **_formatting_note_section_history
    )

_formatting_note_form_template_selection = {
    "spacing": "2",
    "width": "100%",
    "padding": "1em",
    "border_radius": "6px",
    "bg": rx.color("gray", 2),
    "margin_bottom": "1em",
}

def _button_view_all(state: rx.State):
    """
    👁️ Renders "View All" button for templates dialog.
    Visual: Small ghost-variant button that opens all templates dialog
    """
    return rx.button(
        "View All",
        size="1",
        variant="ghost",
        on_click=state.set_show_templates_dialog(True),
    )

def _template_settings_tooltip():
    """
    ⚙️ Renders settings icon with tooltip linking to templates page.
    Visual: Small gear icon button with "Manage Templates" tooltip
    """
    return rx.tooltip(
        rx.link(

            rx.icon_button(

                rx.icon("settings"),
                size="1",
                variant="ghost",
            ),
            href="/templates",
        ),
        content="Manage Templates",
    )

_formatting_view_all_section = {
    "spacing": "2",
    "align_items": "center",
}

_formatting_quick_insert_section = {
    "width": "100%",
    "align_items": "center"
}

def _button_template_selector(state: rx.State, template: dict):
    """
    🔘 Renders a template button for quick insertion.
    Visual: Soft-variant button with template name
    """
    return rx.button(

        template["name"],
        size="2",
        variant="soft",
        on_click=lambda: state.handle_insert_template(template["id"]),
        width="100%",
    )

def _template_search_input(state: rx.State):
    """
    🔍 Renders template search input field.
    Visual: Search box with "Search templates..." placeholder
    """
    return rx.input(
        placeholder="Search templates...",
        value=state.template_search_query,
        on_change=state.set_template_search_query,
        width="100%",
        size="2",
    )

def _no_saved_templates_text():
    """
    📝 Renders placeholder text when no templates exist.
    Visual: Italic gray text prompting user to create templates
    """
    return rx.text(
        "No templates available. Create templates in the Templates page.",
        size="2",
        color=rx.color("gray", 10),
        font_style="italic",
    )

_formatting_template_tooltip = {
    "spacing": "2",
    "width": "100%",
}

_formatting_templates_section = {
    "max_height": "200px",
    "overflow_y": "auto",
    "width": "100%",
    "padding": "0.5em",
    "border_radius": "6px",
    "bg": rx.color("gray", 2)
}

_formatting_templates_tooltips_loop = {
    "spacing": "2",
    "width": "100%",
}

def _template_selector_list(state: rx.State):
    """
    📋 Renders the list of template buttons with tooltips.
    Visual: Search input + scrollable list of template buttons (each with hover tooltip showing content)
    """
    return rx.vstack(

        _template_search_input(state),

        rx.box(

            rx.vstack(

                rx.foreach(

                    state.filtered_templates,

                    lambda template: rx.tooltip(

                        _button_template_selector(state, template),
                        content=template["content"],
                    ),
                ),

                **_formatting_template_tooltip,
            ),

            **_formatting_templates_section,
        ),

        **_formatting_templates_tooltips_loop
    )

def _note_form_template_selection(state: rx.State):
    """
    📑 Renders the template selection section for note form.
    Visual: Header with "Quick Insert from Templates:" + View All/Settings buttons
            + Search input + template list or "no templates" message
    Structure: Conditionally shows template selector list or placeholder
    """
    return rx.vstack(

        rx.hstack(

            rx.text("Quick Insert from Templates:", weight="bold", size="2"),

            rx.spacer(),

            rx.hstack(

                _button_view_all(state),

                _template_settings_tooltip(),

                **_formatting_view_all_section,
            ),

            **_formatting_quick_insert_section,
        ),

        rx.cond(

            # If this isn't empty...
            state.templates,

            # Execute this
            _template_selector_list(state),

            # Otherwise this
            _no_saved_templates_text(),
        ),

        **_formatting_note_form_template_selection
    )

def _note_input_textarea(state: rx.State):
    """
    📝 Renders the note input textarea.
    Visual: Expandable text area for entering note content
    """
    return rx.text_area(
        placeholder="Enter your note here (e.g., 'Recruiter called for phone screen', 'Sent thank you email')...",
        value=state.new_note_text,
        on_change=state.set_new_note_text,
        width="100%",
        min_height="100px",
        resize="vertical",
    )

def _button_add_note(state: rx.State):
    """
    ➕ Renders "Add Note" button.
    Visual: Solid-variant button to submit new note
    """
    return rx.button(
        "Add Note",
        size="3",
        variant="solid",
        on_click=state.handle_add_note,
    )

_formatting_add_note_section = {
    "width": "100%",
    "margin_top": "1em",
}

def _add_note_section(state: rx.State):
    """
    ➕ Renders the "Add Note" button section.
    Visual: Right-aligned "Add Note" button
    """
    return rx.hstack(

        rx.spacer(),
        _button_add_note(state),

        **_formatting_add_note_section
    )

_formatting_section_note_form = {
    "spacing": "3",
    "width": "100%",
}

_formatting_section_note_form_card = {
    "padding": "2em",
    "width": "100%",
    "margin_top": "1em",
}

def _section_note_form(state: rx.State):
    """
    📝 Renders the "Add Note" form card.
    Visual: Card with "Add Note" heading + template selector + textarea + submit button
    """
    return rx.card(

        rx.vstack(

            rx.heading("Add Note", size="4", margin_bottom="1em"),

            _note_form_template_selection(state),

            _note_input_textarea(state),

            _add_note_section(state),

            **_formatting_section_note_form
        ),

        **_formatting_section_note_form_card
    )

def _button_delete_job(state: rx.State):
    """
    🗑️ Renders "Delete Job Application" button.
    Visual: Red soft-variant button that opens deletion confirmation dialog
    """
    return rx.button(
        "Delete Job Application",
        color_scheme="red",
        variant="soft",
        size="2",
        on_click=state.set_show_delete_dialog(True),
    )

def _job_not_found_text():
    """
    ❓ Renders "Job not found" message.
    Visual: Gray text shown when selected_job is None
    """
    return rx.text("Job not found.", size="4", color=rx.color("gray", 10))

def _job_information_card(state: rx.State):
    """
    📇 Renders the complete job information or "not found" message.
    Visual: Full job detail card stack (info + notes + form + delete button) or error text
    Structure: Conditionally shows complete job detail or "Job not found" message
    """
    return rx.cond(

                # If this isn't empty / None...
                state.selected_job,

                # Execute this
                rx.vstack(
                    rx.card(

                        rx.vstack(

                            _company_and_status(state),

                            _job_title(state),

                            rx.divider(margin_y="1em"),

                            _section_details_grid(state),

                            spacing="3",
                            width="100%",
                        ),
                        padding="2em",
                        width="100%",
                    ),

                    _section_note_history(state),

                    _section_note_form(state),

                    # Delete job button
                    rx.box(
                        _button_delete_job(state),

                        margin_top="2em",
                    ),

                    spacing="4",
                    width="100%",
                ),

                # Otherwise execute this
                _job_not_found_text(),
    )

_formatting_job_detail_section = {
    "spacing": "4",
    "padding": "2em",
    "max_width": "900px"
}

def _delete_confirmation_dialog(state: rx.State):
    """
    ⚠️ Renders the delete job confirmation dialog.
    Visual: Alert dialog with "Delete Job Application" title + confirmation message + Cancel/Delete buttons
    """
    return rx.alert_dialog.root(

            rx.alert_dialog.content(

                rx.alert_dialog.title("Delete Job Application"),

                rx.alert_dialog.description("Are you sure? This cannot be undone."),

                rx.flex(
                    rx.alert_dialog.cancel(

                        rx.button("Cancel", variant="soft", on_click=state.set_show_delete_dialog(False)),
                    ),

                    rx.alert_dialog.action(

                        rx.button("Delete", color_scheme="red", on_click=state.handle_delete_job),
                    ),

                    spacing="3",
                ),
            ),

            open=state.show_delete_dialog,
        )

def _button_template_insert(state: rx.State, template: dict):
    """
    📥 Renders "Insert" button in template dialog.
    Visual: Small soft-variant button that inserts template and closes dialog
    """
    return rx.button(
        "Insert",
        size="1",
        variant="soft",
        on_click=lambda: [
            state.handle_insert_template(template["id"]),
            state.set_show_templates_dialog(False),
        ],
    )

_formatting_iteration_box = {
    "spacing": "3",
    "width": "100%"
}

_formatting_lamba_box = {
    "padding": "1em",
    "border_radius": "6px",
    "bg": rx.color("gray", 2),
    "border": f"1px solid {rx.color('gray', 6)}",
    "width": "100%",
}

def _template_name_text(template: dict):
    """
    🏷️ Renders template name text.
    Visual: Bold template name (e.g., "Phone Screen Completed")
    """
    return rx.text(
        template["name"],
        weight="bold",
        size="3",
        flex="1",
    )

_formatting_template_name_and_button = {
    "width": "100%",
    "justify": "between",
    "align_items": "center"
}

def _template_content_text(template: dict):
    """
    📄 Renders template content text.
    Visual: Gray text showing template content preview
    """
    return rx.text(
        template["content"],
        size="2",
        color=rx.color("gray", 11),
    )

_formatting_template_name_button_and_content = {
    "spacing": "2",
    "width": "100%"
}

_formatting_templates_conditional_box = {
    "max_height": "400px",
    "overflow_y": "auto",
    "padding": "1em",
}

def _button_dialog_close(state: rx.State):
    """
    ❌ Renders "Close" button for dialog.
    Visual: Soft-variant "Close" button
    """
    return rx.button(
        "Close",
        variant="soft",
        on_click=state.set_show_templates_dialog(False),
    )

_formatting_button_close = {
    "spacing": "3",
    "margin_top": "1em",
    "justify": "end"
}

def _dialog_close_section(state: rx.State):
    """
    ⬇️ Renders dialog close button section.
    Visual: Right-aligned flex section with close button
    """
    return rx.flex(
        rx.dialog.close(

            _button_dialog_close(state),
        ),

        **_formatting_button_close
    )

def _template_list_item(state: rx.State):
    """
    📋 Renders a single template item in the "View All" dialog.
    Visual: Box with template name + insert button (top) and content preview (bottom)
    """
    return lambda template: rx.box(

        rx.vstack(

            rx.hstack(

                _template_name_text(template),

                _button_template_insert(state, template),

                **_formatting_template_name_and_button,
            ),

            _template_content_text(template),

            **_formatting_template_name_button_and_content,
        ),

        **_formatting_lamba_box,
    )

def _view_all_templates_dialog(state: rx.State):
    """
    📖 Renders the "View All Templates" dialog.
    Visual: Dialog with title + description + scrollable list of templates or "no templates" message + close button
    Structure: Conditionally shows template list or placeholder text
    """
    return rx.dialog.root(

            rx.dialog.content(

                rx.dialog.title("All Templates"),

                rx.dialog.description(
                    "Click on a template name to insert it into your note."
                ),

                rx.box(

                    rx.cond(

                        # If this is not empty / None...
                        state.templates,

                        # Execute this
                        rx.vstack(

                            rx.foreach(

                                # Iterable
                                state.templates,

                                # Main iteration
                                _template_list_item(state),
                            ),

                            **_formatting_iteration_box,
                        ),

                        # Otherwise execute this
                        _no_saved_templates_text(),
                    ),

                    **_formatting_templates_conditional_box,
                ),

                _dialog_close_section(state),
            ),

            open=state.show_templates_dialog,
        )

def render_ui(state: rx.State) -> rx.Component:
    """
    📄 Renders the complete job detail page.
    Visual: Full page with:
            - Color mode toggle (top-right)
            - Page heading with back button
            - Job information card (company, title, details, notes, form)
            - Delete confirmation dialog (hidden until triggered)
            - View all templates dialog (hidden until triggered)
    Structure: Container → VStack → [Heading, Job Info] + Dialogs
    """
    return rx.container(

        rx.color_mode.button(position="top-right"),
        rx.vstack(

            _page_heading(),

            _job_information_card(state),

            **_formatting_job_detail_section,
        ),

        _delete_confirmation_dialog(state),

        _view_all_templates_dialog(state),

        padding="2em",
        min_height="100vh",
    )
