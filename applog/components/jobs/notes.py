import reflex as rx
from typing import Dict

def _timeline_bullet():
    """
    🔵 Renders the circular bullet point on the timeline.
    Visual: A small brown circle that marks each note entry.
    """
    return rx.box(

        rx.box(
            width="12px",
            height="12px",
            border_radius="50%",
            bg=rx.color("brown", 9),
        ),
        width="12px",
        flex_shrink="0",
    )

def _timeline_timestamp(note: Dict):
    """
    📅 Renders the timestamp text for the note.
    Visual: Small gray text showing "DD/MM/YYYY HH:mm" (e.g., "25/12/2025 14:30")
    """
    return rx.text(

        # Format timestamp using rx.moment for proper Var handling
        rx.moment(note["timestamp"], format="DD/MM/YYYY HH:mm"),
        size="1",
        color=rx.color("gray", 10),
        weight="medium",
    )

def _timeline_note_content(note: Dict):
    """
    📝 Renders the actual note content text.
    Visual: Main text body of the note (e.g., "Recruiter called for phone screen")
    """
    return rx.text(
        note["note"],
        size="2",
        color=rx.color("gray", 12),
    )

def _timeline_text_container(note: Dict):
    """
    📦 Vertical container holding timestamp + note content.
    Visual: Stacks the timestamp above the note text with minimal spacing.
    """
    return rx.vstack(

        _timeline_timestamp(note),

        _timeline_note_content(note),

        spacing="1",
        align_items="start",
        flex="1",
    )

def _timeline_item_layout(note: Dict):
    """
    ↔️ Horizontal layout combining bullet + text container.
    Visual: [🔵 bullet] [timestamp + note content]
    """
    return rx.hstack(

        _timeline_bullet(),

        _timeline_text_container(note),

        spacing="3",
        align_items="start",
        width="100%",
    )

_formatting_note_timeline = {
    "padding_left": "1em",
    "border_left": f"2px solid {rx.color('gray', 6)}",
    "padding_bottom": "1.5em",
    "margin_left": "5px",
}

def timeline(note: Dict) -> rx.Component:
    """
    🗓️ Renders a complete timeline item (single note entry).
    Visual: Vertical line on left edge | [🔵] timestamp + note content
    Structure: Outer box with left border + padding, containing the full item layout.
    """

    return rx.box(

        _timeline_item_layout(note),

        **_formatting_note_timeline
    )