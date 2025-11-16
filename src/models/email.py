"""
Email data models using SQLAlchemy.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Email(Base):
    """Model for storing email messages."""

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Microsoft Graph ID
    message_id = Column(String(255), unique=True, nullable=False, index=True)

    # Email metadata
    conversation_id = Column(String(255), index=True)
    subject = Column(String(500))
    sender_email = Column(String(255), index=True)
    sender_name = Column(String(255))

    # Recipients (stored as JSON array)
    to_recipients = Column(JSON)  # List of {"name": "...", "email": "..."}
    cc_recipients = Column(JSON)
    bcc_recipients = Column(JSON)

    # Email content
    body_preview = Column(Text)  # Short preview
    body_text = Column(Text)  # Plain text version
    body_html = Column(Text)  # HTML version

    # Email properties
    is_read = Column(Boolean, default=False)
    is_draft = Column(Boolean, default=False)
    importance = Column(String(50))  # low, normal, high
    has_attachments = Column(Boolean, default=False)

    # Dates
    received_datetime = Column(DateTime, index=True)
    sent_datetime = Column(DateTime)

    # Thread information
    in_reply_to = Column(String(255))

    # Additional metadata from Graph API
    metadata = Column(JSON)

    # Email type (inbox, sent, draft)
    email_type = Column(String(50), index=True)  # inbox, sent, draft

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Email(id={self.id}, subject='{self.subject[:30]}...', from='{self.sender_email}')>"

    def to_dict(self):
        """Convert email to dictionary."""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "subject": self.subject,
            "sender_email": self.sender_email,
            "sender_name": self.sender_name,
            "to_recipients": self.to_recipients,
            "cc_recipients": self.cc_recipients,
            "body_preview": self.body_preview,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "is_read": self.is_read,
            "is_draft": self.is_draft,
            "importance": self.importance,
            "has_attachments": self.has_attachments,
            "received_datetime": self.received_datetime.isoformat() if self.received_datetime else None,
            "sent_datetime": self.sent_datetime.isoformat() if self.sent_datetime else None,
            "email_type": self.email_type,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_graph_api(cls, graph_data: dict, email_type: str = "inbox") -> "Email":
        """
        Create Email instance from Microsoft Graph API response.

        Args:
            graph_data: Email data from Graph API
            email_type: Type of email (inbox, sent, draft)

        Returns:
            Email instance
        """
        # Extract sender info
        sender = graph_data.get("from", {}).get("emailAddress", {})
        sender_email = sender.get("address", "")
        sender_name = sender.get("name", "")

        # Extract recipients
        def parse_recipients(recipients_data):
            if not recipients_data:
                return []
            return [
                {
                    "name": r.get("emailAddress", {}).get("name", ""),
                    "email": r.get("emailAddress", {}).get("address", "")
                }
                for r in recipients_data
            ]

        to_recipients = parse_recipients(graph_data.get("toRecipients"))
        cc_recipients = parse_recipients(graph_data.get("ccRecipients"))
        bcc_recipients = parse_recipients(graph_data.get("bccRecipients"))

        # Parse dates
        received_dt = None
        sent_dt = None

        if graph_data.get("receivedDateTime"):
            try:
                received_dt = datetime.fromisoformat(graph_data["receivedDateTime"].replace("Z", "+00:00"))
            except:
                pass

        if graph_data.get("sentDateTime"):
            try:
                sent_dt = datetime.fromisoformat(graph_data["sentDateTime"].replace("Z", "+00:00"))
            except:
                pass

        # Extract body content
        body = graph_data.get("body", {})
        body_content = body.get("content", "")
        body_type = body.get("contentType", "HTML")

        return cls(
            message_id=graph_data.get("id"),
            conversation_id=graph_data.get("conversationId"),
            subject=graph_data.get("subject", "(No Subject)"),
            sender_email=sender_email,
            sender_name=sender_name,
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            body_preview=graph_data.get("bodyPreview", ""),
            body_text=body_content if body_type == "Text" else "",
            body_html=body_content if body_type == "HTML" else "",
            is_read=graph_data.get("isRead", False),
            is_draft=graph_data.get("isDraft", False),
            importance=graph_data.get("importance", "normal"),
            has_attachments=graph_data.get("hasAttachments", False),
            received_datetime=received_dt,
            sent_datetime=sent_dt,
            in_reply_to=graph_data.get("inReplyTo"),
            email_type=email_type,
            metadata=graph_data  # Store full Graph API response
        )
