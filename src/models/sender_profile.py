"""
Sender profile data models for tracking communication patterns.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from src.models.email import Base


class SenderProfile(Base):
    """Model for storing sender-specific communication profiles."""

    __tablename__ = "sender_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Sender identification
    sender_email = Column(String(255), unique=True, nullable=False, index=True)
    sender_name = Column(String(255))

    # Communication statistics
    total_emails_sent = Column(Integer, default=0)  # Emails you sent to them
    total_emails_received = Column(Integer, default=0)  # Emails received from them
    total_threads = Column(Integer, default=0)  # Number of conversation threads

    # Style metrics
    avg_formality_score = Column(Float)  # 0.0 (casual) to 1.0 (formal)
    avg_response_length = Column(Integer)  # Average word count in your responses
    avg_email_length_received = Column(Integer)  # Their average email length

    # Communication patterns
    preferred_greeting = Column(String(100))  # Most common greeting you use
    preferred_signoff = Column(String(100))  # Most common sign-off you use
    common_topics = Column(JSON)  # List of common discussion topics/keywords

    # Relationship metadata
    relationship_type = Column(String(50))  # colleague, client, manager, friend, etc.
    first_contact_date = Column(DateTime)
    last_interaction_date = Column(DateTime, index=True)

    # Detailed style analysis (JSON)
    style_notes = Column(JSON)  # Detailed patterns: {
    #   "uses_bullets": true/false,
    #   "uses_emojis": true/false,
    #   "tone": "professional"/"casual"/"friendly",
    #   "common_phrases": ["...", "..."],
    #   "email_structure": "...",
    #   etc.
    # }

    # Conversation context
    recent_subjects = Column(JSON)  # Last 5-10 email subjects
    unresolved_threads = Column(Integer, default=0)  # Threads awaiting response

    # AI insights
    ai_generated_summary = Column(Text)  # AI-generated summary of relationship/communication style

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SenderProfile(email='{self.sender_email}', type='{self.relationship_type}')>"

    def to_dict(self):
        """Convert sender profile to dictionary."""
        return {
            "id": self.id,
            "sender_email": self.sender_email,
            "sender_name": self.sender_name,
            "total_emails_sent": self.total_emails_sent,
            "total_emails_received": self.total_emails_received,
            "total_threads": self.total_threads,
            "avg_formality_score": self.avg_formality_score,
            "avg_response_length": self.avg_response_length,
            "preferred_greeting": self.preferred_greeting,
            "preferred_signoff": self.preferred_signoff,
            "common_topics": self.common_topics,
            "relationship_type": self.relationship_type,
            "first_contact_date": self.first_contact_date.isoformat() if self.first_contact_date else None,
            "last_interaction_date": self.last_interaction_date.isoformat() if self.last_interaction_date else None,
            "style_notes": self.style_notes,
            "recent_subjects": self.recent_subjects,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def get_formality_description(self) -> str:
        """Get human-readable formality description."""
        if self.avg_formality_score is None:
            return "Unknown"
        elif self.avg_formality_score < 0.3:
            return "Very Casual"
        elif self.avg_formality_score < 0.5:
            return "Casual"
        elif self.avg_formality_score < 0.7:
            return "Professional"
        else:
            return "Formal"

    def get_response_length_description(self) -> str:
        """Get human-readable response length description."""
        if self.avg_response_length is None:
            return "Unknown"
        elif self.avg_response_length < 50:
            return "Very Brief"
        elif self.avg_response_length < 100:
            return "Brief"
        elif self.avg_response_length < 200:
            return "Moderate"
        else:
            return "Detailed"
