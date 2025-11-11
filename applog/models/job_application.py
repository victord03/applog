"""Job application model."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from applog.database import Base


class ApplicationStatus(str, Enum):
    """Status enum for job applications."""

    APPLIED = "Applied"
    SCREENING = "Screening"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"
    WITHDRAWN = "Withdrawn"
    NO_RESPONSE = "No Response"


class JobApplication(Base):
    """Job application model."""

    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    job_title = Column(String(255), nullable=False)
    job_url = Column(String(500), unique=True, nullable=False)
    location = Column(String(255), index=True)
    description = Column(Text)
    status = Column(
        SQLEnum(ApplicationStatus),
        default=ApplicationStatus.APPLIED,
        nullable=False,
        index=True,
    )
    application_date = Column(DateTime, default=datetime.now, nullable=False)
    salary_range = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    def __repr__(self):
        return f"<JobApplication(id={self.id}, company='{self.company_name}', title='{self.job_title}', status='{self.status.value}')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "job_title": self.job_title,
            "job_url": self.job_url,
            "location": self.location,
            "description": self.description,
            "status": self.status.value,
            "application_date": self.application_date.isoformat()
            if self.application_date
            else None,
            "salary_range": self.salary_range,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
