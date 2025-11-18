"""Service layer for note template operations."""

from sqlalchemy.orm import Session
from applog.models.note_template import NoteTemplate


def validate_template_fields(template_data: dict) -> None:
    """Validate that dictionary is not empty and all field names exist in NoteTemplate model.

    Args:
        template_data: Dictionary containing note template field names and values.

    Raises:
        ValueError: If dictionary is empty or contains invalid field names.
    """
    if not template_data:
        raise ValueError("Dictionary passed is empty (no key values).")

    for key in template_data:
        if not hasattr(NoteTemplate, key):
            raise ValueError(f"Field {key} does not exist. Maybe typo?")


def create_template(session: Session, template_data: dict) -> NoteTemplate:
    """Create a new note template.

    Args:
        session: SQLAlchemy database session.
        template_data: Dictionary containing template data (name, content).

    Returns:
        The created NoteTemplate object with assigned ID.

    Raises:
        ValueError: If template_data is invalid.
    """
    validate_template_fields(template_data)

    # Check required fields
    if "name" not in template_data or not template_data["name"].strip():
        raise ValueError("Template name is required.")
    if "content" not in template_data or not template_data["content"].strip():
        raise ValueError("Template content is required.")

    template = NoteTemplate(**template_data)

    try:
        session.add(template)
        session.commit()
        session.refresh(template)
    except Exception:
        session.rollback()
        raise

    return template


def get_template_by_id(session: Session, template_id: int) -> NoteTemplate | None:
    """Retrieve a note template by its ID.

    Args:
        session: SQLAlchemy database session.
        template_id: The ID of the template to retrieve.

    Returns:
        NoteTemplate object if found, None otherwise.
    """
    return session.get(NoteTemplate, template_id)


def get_all_templates(session: Session) -> list[NoteTemplate]:
    """Retrieve all note templates ordered by name.

    Args:
        session: SQLAlchemy database session.

    Returns:
        List of all NoteTemplate objects.
    """
    return session.query(NoteTemplate).order_by(NoteTemplate.name).all()


def search_templates(session: Session, query: str) -> list[NoteTemplate]:
    """Search templates by name or content.

    Args:
        session: SQLAlchemy database session.
        query: Search query string.

    Returns:
        List of matching NoteTemplate objects.
    """
    if not query or not query.strip():
        return get_all_templates(session)

    search_term = f"%{query.strip()}%"
    return (
        session.query(NoteTemplate)
        .filter(
            (NoteTemplate.name.ilike(search_term))
            | (NoteTemplate.content.ilike(search_term))
        )
        .order_by(NoteTemplate.name)
        .all()
    )


def update_template(
    session: Session, template_id: int, template_updates: dict
) -> NoteTemplate | None:
    """Update an existing note template.

    Args:
        session: SQLAlchemy database session.
        template_id: The ID of the template to update.
        template_updates: Dictionary containing fields to update and their new values.

    Returns:
        Updated NoteTemplate object if template_id exists, None otherwise.

    Raises:
        ValueError: If template_updates is invalid.
    """
    validate_template_fields(template_updates)

    existing_template = get_template_by_id(session, template_id)

    if existing_template is None:
        return None

    for key, value in template_updates.items():
        setattr(existing_template, key, value)

    try:
        session.commit()
        session.refresh(existing_template)
    except Exception:
        session.rollback()
        raise

    return existing_template


def delete_template(session: Session, template_id: int) -> bool:
    """Delete a note template from the database.

    Args:
        session: SQLAlchemy database session.
        template_id: The ID of the template to delete.

    Returns:
        True if deletion succeeded, False if template_id doesn't exist.
    """
    existing_template = get_template_by_id(session, template_id)

    if existing_template is None:
        return False

    try:
        session.delete(existing_template)
        session.commit()
    except Exception:
        session.rollback()
        raise

    return True
