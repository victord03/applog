import reflex as rx

def _filter_sidebar_heading():
    """
    🔤 Renders the "Filters" heading for the sidebar.
    Visual: Bold "Filters" heading with spacing below
    """
    return rx.heading("Filters", size="4", margin_bottom="1em")

def _company_filter(state: rx.State):
    """
    🏢 Renders the Company filter dropdown.
    Visual: Label "Company" + select dropdown with all unique company names
    """
    return rx.vstack(
                rx.text("Company", weight="bold", size="2"),
                rx.select(
                    state.unique_companies,
                    value=state.selected_company,
                    on_change=state.set_selected_company,
                    width="100%",
                ),

                spacing="2",
                align_items="start",
                width="100%",
            ),

def _status_filter(state: rx.State):
    """
    🏷️ Renders the Status filter dropdown.
    Visual: Label "Status" + select dropdown with all unique status values
    """
    return rx.vstack(
                rx.text("Status", weight="bold", size="2"),
                rx.select(
                    state.unique_statuses,
                    value=state.selected_status,
                    on_change=state.set_selected_status,
                    width="100%",
                ),
                spacing="2",
                align_items="start",
                width="100%",
            ),

def _location_filter(state: rx.State):
    """
    📍 Renders the Location filter dropdown.
    Visual: Label "Location" + select dropdown with all unique location values
    """
    return rx.vstack(
        rx.text("Location", weight="bold", size="2"),
        rx.select(
            state.unique_locations,
            value=state.selected_location,
            on_change=state.set_selected_location,
            width="100%",
        ),
        spacing="2",
        align_items="start",
        width="100%",
    )

_vstack_layout = {
    "spacing": "4",
    "align_items": "start",
    "width": "100%",
}

_formatting_filter_sidebar = {
    "padding": "1.5em",
    "border_radius": "8px",
    "bg": rx.color("gray", 2),
    "border": f"1px solid {rx.color('gray', 6)}",
    "min_width": "250px",
}

def sb_filter(state: rx.State) -> rx.Component:
    """
    📊 Renders the complete filter sidebar.
    Visual: Gray-background sidebar box containing:
            - "Filters" heading
            - Company filter dropdown
            - Status filter dropdown
            - Location filter dropdown
    Structure: Box (with border/padding/bg) → VStack → [Heading, Filters]
    """
    return rx.box(

        rx.vstack(

            _filter_sidebar_heading(),

            _company_filter(state),

            _status_filter(state),

            _location_filter(state),

            **_vstack_layout
        ),

        **_formatting_filter_sidebar
    )