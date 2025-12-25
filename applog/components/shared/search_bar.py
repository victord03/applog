import reflex as rx

def search_bar(state: rx.State) -> rx.Component:
    """Search bar component."""
    return rx.input(
        placeholder="Search by company or job title...",
        value=state.search_query,
        on_change=state.set_search_query,
        width="100%",
        size="3",
    )