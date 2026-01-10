import reflex as rx

from applog.components.templates import template_form

def _templates_list_edit_button(state: rx.State, template) -> rx.Component:
    """
    ✏️ Renders the "Edit" button for a template item.
    Visual: Small soft button labeled "Edit" that opens edit mode.
    """
    return rx.button(
        "Edit",
        size="1",
        variant="soft",
        on_click=lambda: state.handle_edit_template(
            template["id"]
        ),
    )

def _templates_list_delete_button(state: rx.State, template) -> rx.Component:
    """
    🗑️ Renders the "Delete" button for a template item.
    Visual: Small red soft button labeled "Delete" that shows confirmation dialog.
    """
    return rx.button(
        "Delete",
        size="1",
        variant="soft",
        color_scheme="red",
        on_click=lambda: [
            state.set_selected_template_id(
                template["id"]
            ),
            state.set_show_delete_template_dialog(
                True
            ),
        ],
    )

_formatting_templates_list_hstack = {
    "justify": "between",
    "width": "100%"
}

_formatting_templates_list_vstack = {
    "spacing": "2",
    "width": "100%"
}

_formatting_templates_list_box = {
    "padding": "1em",
    "border_radius": "6px",
    "bg": rx.color("gray", 2),
    "border": f"1px solid {rx.color('gray', 6)}",
    "width": "100%"
}

def _templates_list_delete_confirmation_dialog_cancel_button(state: rx.State):
    """
    ❌ Renders the "Cancel" button in the delete confirmation dialog.
    Visual: Soft "Cancel" button that closes the dialog.
    """
    return rx.button(
        "Cancel",
        variant="soft",
        on_click=state.set_show_delete_template_dialog(False),
    )

def _templates_list_delete_confirmation_dialog_delete_button(state: rx.State):
    """
    🗑️ Renders the "Delete" button in the delete confirmation dialog.
    Visual: Red "Delete" button that permanently removes the template.
    """
    return rx.alert_dialog.action(
        rx.button(
            "Delete",
            color_scheme="red",
            on_click=state.handle_delete_template,
        ),
    )

_formatting_templates_list_display = {
    "spacing": "3",
    "width": "100%"
}

_formatting_templates_list_card = {
    "padding": "2em",
    "width": "100%",
    "margin_top": "1em"
}

_formatting_templates_list_container_vstack = {
    "spacing": "4",
    "padding": "2em",
    "max_width": "900px"
}

_formatting_templates_list_container = {
    "padding": "2em",
    "min_height": "100vh"
}

def _templates_list_delete_confirmation_dialog(state: rx.State):
    """
    ⚠️ Renders the delete confirmation alert dialog.
    Visual: Modal dialog with "Delete Template" title, warning message,
            and [Cancel] [Delete] buttons.
    """
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Delete Template"),
            rx.alert_dialog.description(
                "Are you sure? This cannot be undone."
            ),
            rx.flex(
                rx.alert_dialog.cancel(

                    _templates_list_delete_confirmation_dialog_cancel_button(state),
                ),

                _templates_list_delete_confirmation_dialog_delete_button(state),

                spacing="3",
            ),
        ),
        open=state.show_delete_template_dialog,
    )

def _templates_list_no_templates_found_text() -> rx.Component:
    """
    📭 Renders the empty state message when no templates exist.
    Visual: Italic gray text "No templates found. Add one above!"
    """
    return rx.text(
        "No templates found. Add one above!",
        size="2",
        color=rx.color("gray", 10),
        font_style="italic",
    )

def _templates_list_display_templates_lambda_function(state: rx.State):
    """
    📋 Returns a lambda function for rendering individual template items.
    Visual: Box containing [template name] [Edit] [Delete]
                           [template content preview]
    Used by rx.foreach to iterate over filtered templates.
    """
    return lambda template: rx.box(

        rx.vstack(

            rx.hstack(

                rx.heading(
                    template["name"], size="4", flex="1"
                ),

                rx.hstack(

                    _templates_list_edit_button(state, template),

                    _templates_list_delete_button(state, template),

                    spacing="2",
                ),

                **_formatting_templates_list_hstack
            ),

            rx.text(
                template["content"],
                size="2",
                color=rx.color("gray", 11),
            ),

            **_formatting_templates_list_vstack
        ),

        **_formatting_templates_list_box
    )

def _filter_templates_conditional(state: rx.State):
    """
    🔍 Renders the templates list or empty state conditionally.
    Visual: If templates exist, shows list of template cards.
            If no templates, shows "No templates found" message.
    """
    return rx.cond(

        # Cond 1: If this is true
        state.filtered_templates,

        # Cond 1: Run this
        rx.vstack(

            # Loop
            rx.foreach(

                # Iterable
                state.filtered_templates,

                # Lambda function
                _templates_list_display_templates_lambda_function(state),
            ),

            **_formatting_templates_list_display
        ),

        # Cond 1: Otherwise run this
        _templates_list_no_templates_found_text(),
    )


def render_ui(state: rx.State) -> rx.Component:
    """
    📋 Renders the complete templates management page.
    Visual: Full page container with heading, search bar, form, templates list,
            and delete confirmation dialog.
    """
    return rx.container(

        rx.color_mode.button(position="top-right"),

        rx.vstack(

            *template_form.render_form(state),

            # Templates list
            rx.card(

                rx.vstack(

                    rx.heading("Your Templates", size="5", margin_bottom="1em"),

                    # Cond 1: Declaration
                    _filter_templates_conditional(state),

                    **_formatting_templates_list_display
                ),

                **_formatting_templates_list_card
            ),

            **_formatting_templates_list_container_vstack
        ),

        # Delete confirmation dialog
        _templates_list_delete_confirmation_dialog(state),

        **_formatting_templates_list_container
    )
