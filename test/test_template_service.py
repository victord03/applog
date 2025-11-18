"""Unit tests for template service."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from applog.database import Base
from applog.models.note_template import NoteTemplate
from applog.services.template_service import (
    create_template,
    get_template_by_id,
    get_all_templates,
    search_templates,
    update_template,
    delete_template,
)


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestCreateTemplate:
    """Tests for create_template function."""

    def test_create_template_stores_in_database(self, db_session):
        """Test that create_template successfully stores a template."""
        template_data = {
            "name": "Follow-up Email",
            "content": "Sent follow-up email to recruiter.",
        }

        result = create_template(db_session, template_data)

        assert result.id is not None
        assert result.name == "Follow-up Email"
        assert result.content == "Sent follow-up email to recruiter."
        assert result.created_at is not None
        assert result.updated_at is not None

    def test_create_template_empty_data_raises_error(self, db_session):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError, match="Dictionary passed is empty"):
            create_template(db_session, {})

    def test_create_template_invalid_field_raises_error(self, db_session):
        """Test that invalid field names raise ValueError."""
        template_data = {
            "name": "Test",
            "content": "Test content",
            "invalid_field": "value",
        }

        with pytest.raises(ValueError, match="Field invalid_field does not exist"):
            create_template(db_session, template_data)

    def test_create_template_missing_name_raises_error(self, db_session):
        """Test that missing name raises ValueError."""
        template_data = {"content": "Test content"}

        with pytest.raises(ValueError, match="Template name is required"):
            create_template(db_session, template_data)

    def test_create_template_missing_content_raises_error(self, db_session):
        """Test that missing content raises ValueError."""
        template_data = {"name": "Test"}

        with pytest.raises(ValueError, match="Template content is required"):
            create_template(db_session, template_data)

    def test_create_template_empty_name_raises_error(self, db_session):
        """Test that empty name raises ValueError."""
        template_data = {"name": "   ", "content": "Test content"}

        with pytest.raises(ValueError, match="Template name is required"):
            create_template(db_session, template_data)


class TestReadTemplate:
    """Tests for template read functions."""

    def test_get_template_by_id_returns_template_when_exists(self, db_session):
        """Test retrieving existing template by ID."""
        template = NoteTemplate(
            name="Phone Screen", content="Completed phone screen with recruiter."
        )
        db_session.add(template)
        db_session.commit()

        result = get_template_by_id(db_session, template.id)

        assert result is not None
        assert result.id == template.id
        assert result.name == "Phone Screen"

    def test_get_template_by_id_returns_none_when_not_found(self, db_session):
        """Test that non-existent ID returns None."""
        result = get_template_by_id(db_session, 999)
        assert result is None

    def test_get_all_templates_returns_all_ordered_by_name(self, db_session):
        """Test get_all_templates returns all templates in alphabetical order."""
        templates = [
            NoteTemplate(name="Z Template", content="Last"),
            NoteTemplate(name="A Template", content="First"),
            NoteTemplate(name="M Template", content="Middle"),
        ]
        for t in templates:
            db_session.add(t)
        db_session.commit()

        result = get_all_templates(db_session)

        assert len(result) == 3
        assert result[0].name == "A Template"
        assert result[1].name == "M Template"
        assert result[2].name == "Z Template"

    def test_search_templates_by_name(self, db_session):
        """Test searching templates by name."""
        templates = [
            NoteTemplate(name="Cover Letter Sent", content="Sent cover letter"),
            NoteTemplate(name="Phone Screen", content="Completed phone screen"),
            NoteTemplate(name="Cover Letter Follow-up", content="Follow-up sent"),
        ]
        for t in templates:
            db_session.add(t)
        db_session.commit()

        result = search_templates(db_session, "cover")

        assert len(result) == 2
        assert all("cover" in t.name.lower() for t in result)

    def test_search_templates_by_content(self, db_session):
        """Test searching templates by content."""
        templates = [
            NoteTemplate(name="Template 1", content="Sent follow-up email"),
            NoteTemplate(name="Template 2", content="Completed interview"),
            NoteTemplate(name="Template 3", content="Sent thank you email"),
        ]
        for t in templates:
            db_session.add(t)
        db_session.commit()

        result = search_templates(db_session, "email")

        assert len(result) == 2
        assert all("email" in t.content.lower() for t in result)

    def test_search_templates_empty_query_returns_all(self, db_session):
        """Test that empty search query returns all templates."""
        templates = [
            NoteTemplate(name="Template 1", content="Content 1"),
            NoteTemplate(name="Template 2", content="Content 2"),
        ]
        for t in templates:
            db_session.add(t)
        db_session.commit()

        result = search_templates(db_session, "")

        assert len(result) == 2


class TestUpdateTemplate:
    """Tests for update_template function."""

    def test_update_template_modifies_fields(self, db_session):
        """Test updating template fields."""
        template = NoteTemplate(name="Old Name", content="Old content")
        db_session.add(template)
        db_session.commit()

        updates = {"name": "New Name", "content": "New content"}
        result = update_template(db_session, template.id, updates)

        assert result is not None
        assert result.name == "New Name"
        assert result.content == "New content"

    def test_update_template_invalid_field_raises_error(self, db_session):
        """Test that invalid field raises ValueError."""
        template = NoteTemplate(name="Test", content="Test content")
        db_session.add(template)
        db_session.commit()

        updates = {"invalid_field": "value"}

        with pytest.raises(ValueError, match="Field invalid_field does not exist"):
            update_template(db_session, template.id, updates)

    def test_update_template_empty_dict_raises_error(self, db_session):
        """Test that empty updates dict raises ValueError."""
        template = NoteTemplate(name="Test", content="Test content")
        db_session.add(template)
        db_session.commit()

        with pytest.raises(ValueError, match="Dictionary passed is empty"):
            update_template(db_session, template.id, {})

    def test_update_template_nonexistent_id_returns_none(self, db_session):
        """Test updating non-existent template returns None."""
        result = update_template(db_session, 999, {"name": "Test"})
        assert result is None


class TestDeleteTemplate:
    """Tests for delete_template function."""

    def test_delete_template_success(self, db_session):
        """Test successful template deletion."""
        template = NoteTemplate(name="To Delete", content="Delete this")
        db_session.add(template)
        db_session.commit()
        template_id = template.id

        result = delete_template(db_session, template_id)

        assert result is True
        assert get_template_by_id(db_session, template_id) is None

    def test_delete_template_nonexistent_returns_false(self, db_session):
        """Test deleting non-existent template returns False."""
        result = delete_template(db_session, 999)
        assert result is False
