"""
Database service for managing SQLite database operations.
Handles CRUD operations for emails, sender profiles, drafts, and settings.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from contextlib import contextmanager

from sqlalchemy import create_engine, func, desc, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from src.config import get_settings
from src.models.email import Base, Email
from src.models.sender_profile import SenderProfile
from src.models.draft import Draft, StyleProfile, AppSetting

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations."""

    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection and create tables."""
        logger.info(f"Initializing database: {self.settings.database_url}")

        try:
            # Create engine
            self.engine = create_engine(
                self.settings.database_url,
                connect_args={"check_same_thread": False},  # For SQLite
                echo=self.settings.DEBUG_MODE  # Log SQL queries in debug mode
            )

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database initialized successfully")

            # Initialize default style profile if not exists
            with self.get_session() as session:
                profile = session.query(StyleProfile).filter_by(profile_name="default").first()
                if not profile:
                    profile = StyleProfile(profile_name="default", is_active=1)
                    session.add(profile)
                    session.commit()
                    logger.info("Created default style profile")

        except Exception as e:
            logger.exception(f"Failed to initialize database: {e}")
            raise

    @contextmanager
    def get_session(self) -> Session:
        """
        Get a database session with automatic cleanup.

        Usage:
            with db_service.get_session() as session:
                # Use session
                pass
        """
        session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ==================== Email Operations ====================

    def save_email(self, email: Email) -> Email:
        """Save or update an email."""
        with self.get_session() as session:
            # Check if email already exists
            existing = session.query(Email).filter_by(message_id=email.message_id).first()

            if existing:
                # Update existing email
                for key, value in email.__dict__.items():
                    if not key.startswith("_"):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(existing)
                logger.debug(f"Updated email: {email.message_id}")
                return existing
            else:
                # Insert new email
                session.add(email)
                session.commit()
                session.refresh(email)
                logger.debug(f"Saved new email: {email.message_id}")
                return email

    def save_emails_batch(self, emails: List[Email]) -> int:
        """Save multiple emails in a batch."""
        count = 0
        with self.get_session() as session:
            for email in emails:
                existing = session.query(Email).filter_by(message_id=email.message_id).first()
                if not existing:
                    session.add(email)
                    count += 1

            session.commit()
            logger.info(f"Saved {count} new emails (out of {len(emails)} total)")
            return count

    def get_email_by_message_id(self, message_id: str) -> Optional[Email]:
        """Get email by Microsoft Graph message ID."""
        with self.get_session() as session:
            return session.query(Email).filter_by(message_id=message_id).first()

    def get_emails_by_type(
        self,
        email_type: str,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Email]:
        """Get emails by type (inbox, sent, draft)."""
        with self.get_session() as session:
            query = session.query(Email).filter_by(email_type=email_type)

            if unread_only:
                query = query.filter_by(is_read=False)

            query = query.order_by(desc(Email.received_datetime))
            query = query.limit(limit).offset(offset)

            return query.all()

    def get_emails_by_sender(self, sender_email: str, limit: int = 50) -> List[Email]:
        """Get all emails from a specific sender."""
        with self.get_session() as session:
            return (
                session.query(Email)
                .filter_by(sender_email=sender_email)
                .order_by(desc(Email.received_datetime))
                .limit(limit)
                .all()
            )

    def get_email_thread(self, conversation_id: str) -> List[Email]:
        """Get all emails in a conversation thread."""
        with self.get_session() as session:
            return (
                session.query(Email)
                .filter_by(conversation_id=conversation_id)
                .order_by(Email.received_datetime)
                .all()
            )

    def get_sent_emails_for_analysis(self, limit: int = 200) -> List[Email]:
        """Get sent emails for style analysis."""
        with self.get_session() as session:
            return (
                session.query(Email)
                .filter_by(email_type="sent")
                .order_by(desc(Email.sent_datetime))
                .limit(limit)
                .all()
            )

    def search_emails(
        self,
        query: str,
        email_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Email]:
        """Search emails by subject or body content."""
        with self.get_session() as session:
            search_filter = or_(
                Email.subject.like(f"%{query}%"),
                Email.body_text.like(f"%{query}%"),
                Email.body_preview.like(f"%{query}%")
            )

            if email_type:
                search_filter = and_(search_filter, Email.email_type == email_type)

            return (
                session.query(Email)
                .filter(search_filter)
                .order_by(desc(Email.received_datetime))
                .limit(limit)
                .all()
            )

    # ==================== Sender Profile Operations ====================

    def get_or_create_sender_profile(self, sender_email: str, sender_name: str = "") -> SenderProfile:
        """Get existing sender profile or create new one."""
        with self.get_session() as session:
            profile = session.query(SenderProfile).filter_by(sender_email=sender_email).first()

            if not profile:
                profile = SenderProfile(
                    sender_email=sender_email,
                    sender_name=sender_name,
                    first_contact_date=datetime.utcnow(),
                    style_notes={}
                )
                session.add(profile)
                session.commit()
                session.refresh(profile)
                logger.info(f"Created new sender profile: {sender_email}")

            return profile

    def update_sender_profile(self, sender_email: str, **kwargs) -> Optional[SenderProfile]:
        """Update sender profile with new data."""
        with self.get_session() as session:
            profile = session.query(SenderProfile).filter_by(sender_email=sender_email).first()

            if profile:
                for key, value in kwargs.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)

                profile.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(profile)
                logger.debug(f"Updated sender profile: {sender_email}")
                return profile

            return None

    def get_all_sender_profiles(self, limit: int = 100) -> List[SenderProfile]:
        """Get all sender profiles, ordered by last interaction."""
        with self.get_session() as session:
            return (
                session.query(SenderProfile)
                .order_by(desc(SenderProfile.last_interaction_date))
                .limit(limit)
                .all()
            )

    def get_top_senders(self, limit: int = 20) -> List[SenderProfile]:
        """Get most frequent senders."""
        with self.get_session() as session:
            return (
                session.query(SenderProfile)
                .order_by(desc(SenderProfile.total_emails_received))
                .limit(limit)
                .all()
            )

    # ==================== Draft Operations ====================

    def save_draft(self, draft: Draft) -> Draft:
        """Save a draft email."""
        with self.get_session() as session:
            session.add(draft)
            session.commit()
            session.refresh(draft)
            logger.info(f"Saved draft (version {draft.draft_version})")
            return draft

    def get_drafts_for_email(self, original_email_id: str) -> List[Draft]:
        """Get all draft versions for an email."""
        with self.get_session() as session:
            return (
                session.query(Draft)
                .filter_by(original_email_id=original_email_id)
                .order_by(Draft.draft_version)
                .all()
            )

    def get_latest_draft_for_email(self, original_email_id: str) -> Optional[Draft]:
        """Get the most recent draft for an email."""
        with self.get_session() as session:
            return (
                session.query(Draft)
                .filter_by(original_email_id=original_email_id)
                .order_by(desc(Draft.draft_version))
                .first()
            )

    def update_draft_feedback(self, draft_id: int, was_used: int, user_edits: str = None, rating: int = None):
        """Update draft with user feedback."""
        with self.get_session() as session:
            draft = session.query(Draft).filter_by(id=draft_id).first()
            if draft:
                draft.was_used = was_used
                if user_edits:
                    draft.user_edits = user_edits
                if rating:
                    draft.user_rating = rating
                draft.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated draft feedback: {draft_id}")

    # ==================== Style Profile Operations ====================

    def get_active_style_profile(self) -> Optional[StyleProfile]:
        """Get the active user style profile."""
        with self.get_session() as session:
            return session.query(StyleProfile).filter_by(is_active=1).first()

    def update_style_profile(self, **kwargs) -> Optional[StyleProfile]:
        """Update the active style profile."""
        with self.get_session() as session:
            profile = session.query(StyleProfile).filter_by(is_active=1).first()

            if profile:
                for key, value in kwargs.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)

                profile.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(profile)
                logger.info("Updated style profile")
                return profile

            return None

    # ==================== App Settings Operations ====================

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get application setting by key."""
        with self.get_session() as session:
            setting = session.query(AppSetting).filter_by(key=key).first()
            return setting.value if setting else default

    def set_setting(self, key: str, value: str, description: str = ""):
        """Set application setting."""
        with self.get_session() as session:
            setting = session.query(AppSetting).filter_by(key=key).first()

            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = AppSetting(key=key, value=value, description=description)
                session.add(setting)

            session.commit()
            logger.debug(f"Set setting: {key} = {value}")

    # ==================== Statistics & Analytics ====================

    def get_email_stats(self) -> Dict[str, Any]:
        """Get email statistics."""
        with self.get_session() as session:
            total_emails = session.query(Email).count()
            total_inbox = session.query(Email).filter_by(email_type="inbox").count()
            total_sent = session.query(Email).filter_by(email_type="sent").count()
            total_unread = session.query(Email).filter_by(is_read=False).count()

            return {
                "total_emails": total_emails,
                "total_inbox": total_inbox,
                "total_sent": total_sent,
                "total_unread": total_unread
            }

    def get_sender_stats(self) -> Dict[str, Any]:
        """Get sender statistics."""
        with self.get_session() as session:
            total_senders = session.query(SenderProfile).count()
            avg_formality = session.query(func.avg(SenderProfile.avg_formality_score)).scalar()

            return {
                "total_senders": total_senders,
                "avg_formality_score": avg_formality
            }

    def cleanup_old_data(self, days: int = 90):
        """Clean up old emails and drafts."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with self.get_session() as session:
            # Delete old emails
            old_emails = session.query(Email).filter(Email.created_at < cutoff_date).delete()

            # Delete old drafts
            old_drafts = session.query(Draft).filter(Draft.created_at < cutoff_date).delete()

            session.commit()
            logger.info(f"Cleaned up {old_emails} old emails and {old_drafts} old drafts")


# Global instance
_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get or create the global DatabaseService instance."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
