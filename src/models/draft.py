"""
Draft email data models for tracking generated and refined drafts.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from src.models.email import Base


class Draft(Base):
    """Model for storing draft emails and their revision history."""

    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Reference to original email
    original_email_id = Column(String(255), index=True)  # Graph API message ID
    conversation_id = Column(String(255), index=True)

    # Draft metadata
    draft_version = Column(Integer, default=1)  # Version number (1, 2, 3, etc.)
    parent_draft_id = Column(Integer)  # ID of previous version (for refinements)

    # Draft content
    subject = Column(String(500))
    body_content = Column(Text, nullable=False)
    content_type = Column(String(20), default="HTML")  # HTML or Text

    # Generation metadata
    ai_model_used = Column(String(100))  # e.g., "claude-3-5-sonnet-20241022"
    prompt_used = Column(Text)  # The prompt sent to AI
    refinement_instruction = Column(Text)  # User's refinement instruction (if any)
    tokens_used = Column(Integer)  # API token usage

    # Style/tone settings used
    target_formality = Column(String(50))  # casual, professional, formal
    target_length = Column(String(50))  # short, medium, long
    style_preferences = Column(JSON)  # Additional style settings used

    # User feedback
    user_rating = Column(Integer)  # 1-5 stars (optional)
    was_used = Column(Integer, default=0)  # 0=not used, 1=used as-is, 2=edited then used
    user_edits = Column(Text)  # If user edited, store the final version

    # Status
    status = Column(String(50), default="generated")  # generated, refined, sent, discarded

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime)  # When the draft was sent (if sent)

    def __repr__(self):
        return f"<Draft(id={self.id}, version={self.draft_version}, status='{self.status}')>"

    def to_dict(self):
        """Convert draft to dictionary."""
        return {
            "id": self.id,
            "original_email_id": self.original_email_id,
            "conversation_id": self.conversation_id,
            "draft_version": self.draft_version,
            "parent_draft_id": self.parent_draft_id,
            "subject": self.subject,
            "body_content": self.body_content,
            "content_type": self.content_type,
            "ai_model_used": self.ai_model_used,
            "refinement_instruction": self.refinement_instruction,
            "tokens_used": self.tokens_used,
            "target_formality": self.target_formality,
            "target_length": self.target_length,
            "user_rating": self.user_rating,
            "was_used": self.was_used,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None
        }


class StyleProfile(Base):
    """Model for storing user's overall writing style profile."""

    __tablename__ = "style_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Profile metadata
    profile_name = Column(String(100), default="default")  # Allow multiple profiles in future
    is_active = Column(Integer, default=1)

    # Overall statistics
    total_emails_analyzed = Column(Integer, default=0)
    last_analysis_date = Column(DateTime)

    # Style metrics
    avg_email_length = Column(Integer)  # Average word count
    avg_formality_score = Column(Float)  # 0.0 to 1.0
    avg_readability_score = Column(Float)  # Flesch reading ease

    # Common patterns
    common_greetings = Column(JSON)  # List of greetings with frequency
    common_signoffs = Column(JSON)  # List of sign-offs with frequency
    common_phrases = Column(JSON)  # Frequently used phrases

    # Writing characteristics
    uses_bullet_points = Column(Integer, default=0)  # 0=rarely, 1=sometimes, 2=often
    uses_numbered_lists = Column(Integer, default=0)
    uses_emojis = Column(Integer, default=0)
    paragraph_style = Column(String(50))  # short, medium, long

    # Tone descriptors
    tone_descriptors = Column(JSON)  # ["professional", "friendly", "direct", etc.]

    # Detailed style analysis
    style_analysis = Column(JSON)  # Comprehensive style data: {
    #   "sentence_complexity": "...",
    #   "active_vs_passive": "...",
    #   "vocabulary_level": "...",
    #   "punctuation_patterns": {...},
    #   etc.
    # }

    # AI-generated style summary
    style_summary = Column(Text)  # Natural language summary of writing style

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<StyleProfile(name='{self.profile_name}', emails_analyzed={self.total_emails_analyzed})>"

    def to_dict(self):
        """Convert style profile to dictionary."""
        return {
            "id": self.id,
            "profile_name": self.profile_name,
            "total_emails_analyzed": self.total_emails_analyzed,
            "avg_email_length": self.avg_email_length,
            "avg_formality_score": self.avg_formality_score,
            "common_greetings": self.common_greetings,
            "common_signoffs": self.common_signoffs,
            "common_phrases": self.common_phrases,
            "uses_bullet_points": self.uses_bullet_points,
            "uses_emojis": self.uses_emojis,
            "paragraph_style": self.paragraph_style,
            "tone_descriptors": self.tone_descriptors,
            "style_summary": self.style_summary,
            "last_analysis_date": self.last_analysis_date.isoformat() if self.last_analysis_date else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AppSetting(Base):
    """Model for storing application settings."""

    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text)
    description = Column(String(500))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AppSetting(key='{self.key}', value='{self.value[:50]}...')>"
