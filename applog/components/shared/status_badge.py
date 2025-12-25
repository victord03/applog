import reflex as rx

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
