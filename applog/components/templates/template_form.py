import reflex as rx

_formatting_heading = {
    "width": "100%",
    "align_items": "center",
    "margin_bottom": "2em",
}

def _heading() -> rx.Component:
    """
    📋 Renders the page header with title and back button.
    Visual: [Note Templates (large)]    [spacer]    [← Back to Jobs button]
    """
    return rx.hstack(
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

        **_formatting_heading
    )

def _search_bar_input(state: rx.State) -> rx.Component:
    """
    🔍 Renders the template search input field.
    Visual: Search box with placeholder "Search templates by name or content..."
    """
    return rx.input(
                placeholder="Search templates by name or content...",
                value=state.template_search_query,
                on_change=state.set_template_search_query,
                width="100%",
                size="3",
                margin_bottom="1em",
            )

def _message_display(state: rx.State) -> rx.Component:
    """
    💬 Renders success or error messages conditionally.
    Visual: Green callout for success, red callout for errors (appears when state.form_message is set)
    """
    return rx.cond(

        # Cond 1: If this is true
        state.form_message,

        # Cond 1: Run this
        # Cond 2: Declaration
        rx.cond(

            # Cond 2: If this is true
            state.form_message_type == "success",

            # Cond 2: Run this
            rx.callout(
                state.form_message,
                icon="info",
                color_scheme="green",
                size="2",
            ),

            # Cond 2: Otherwise run this
            rx.callout(
                state.form_message,
                icon="alert-triangle",
                color_scheme="red",
                size="2",
            ),
        ),
    )

def _form_actions(state: rx.State) -> rx.Component:
    """
    🎬 Renders form action buttons (Cancel/Save or Update).
    Visual: [Cancel button (if editing)]    [spacer]    [Add/Update Template button]
    """
    return rx.hstack(
        rx.cond(
            state.template_edit_mode,
            rx.button(
                "Cancel",
                variant="soft",
                size="3",
                on_click=state.clear_template_form,
            ),
        ),
        rx.spacer(),
        rx.button(
            rx.cond(
                state.template_edit_mode,
                "Update Template",
                "Add Template",
            ),
            size="3",
            variant="solid",
            on_click=state.handle_template_submit,
        ),
        width="100%",
        margin_top="1em",
    )

_formatting_template_form_vstacks = {
    "spacing": "2",
    "align_items": "start",
    "width": "100%"
}

_formatting_template_form_heading = {
    "size": "5",
    "margin_bottom": "1em"
}

def _template_name_input(state: rx.State) -> rx.Component:
    """
    📝 Renders the template name input field.
    Visual: Text input for template name (e.g., "Cover Letter Sent")
    """
    return rx.input(
        placeholder="e.g., Cover Letter Sent, Phone Screen Completed",
        value=state.form_template_name,
        on_change=state.set_form_template_name,
        width="100%",
        size="3",
    )

def _template_content_text_area(state: rx.State) -> rx.Component:
    """
    📄 Renders the template content textarea.
    Visual: Multi-line text area for template content (vertically resizable)
    """
    return rx.text_area(
        placeholder="The note text that will be inserted...",
        value=state.form_template_content,
        on_change=state.set_form_template_content,
        width="100%",
        min_height="100px",
        resize="vertical",
    )

_formatting_template_form_card_vstack = {
    "spacing": "4",
    "width": "100%"
}

_formatting_template_form_card = {
    "padding": "2em",
    "width": "100%"
}

def _template_form(state: rx.State) -> rx.Component:
    """
    📋 Renders the complete template form card.
    Visual: Card containing heading (Add/Edit), name input, content textarea,
            message display, and action buttons.
    """
    return rx.card(

        rx.vstack(

            rx.heading(

                rx.cond(
                    state.template_edit_mode,
                    "Edit Template",
                    "Add New Template",
                ),

                **_formatting_template_form_heading
            ),

            rx.vstack(

                rx.text("Template Name", weight="bold", size="2"),

                _template_name_input(state),

                **_formatting_template_form_vstacks
            ),

            rx.vstack(

                rx.text("Template Content", weight="bold", size="2"),

                _template_content_text_area(state),

                **_formatting_template_form_vstacks
            ),

            # Message display
            _message_display(state),

            # Form actions
            _form_actions(state),

            **_formatting_template_form_card_vstack
        ),

        **_formatting_template_form_card
    )


def render_form(state: rx.State) -> list[rx.Component]:
    """
    🎨 Returns the list of template form components.
    Returns: List containing [heading, search bar, template form card]
    Used by template_list.py to compose the full templates page.
    """
    return [
        _heading(),
        _search_bar_input(state),
        _template_form(state)
    ]
