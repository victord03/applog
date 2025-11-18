"""Note template model."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from applog.database import Base


class NoteTemplate(Base):
    """Note template model for storing reusable note templates."""

    __tablename__ = "note_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    def __repr__(self):
        return f"<NoteTemplate(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
