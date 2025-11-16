"""
Draft generator service - orchestrates AI, style learning, and database services
to generate contextual email drafts.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.services.ai_service import get_ai_service, REFINEMENT_PRESETS
from src.services.db_service import get_db_service
from src.services.style_learning import get_style_learning_service
from src.models.email import Email
from src.models.draft import Draft
from src.utils.text_processing import clean_email_text, extract_email_body_only

logger = logging.getLogger(__name__)


class DraftGenerator:
    """Orchestrates draft generation with full context awareness."""

    def __init__(self):
        self.ai_service = get_ai_service()
        self.db_service = get_db_service()
        self.style_service = get_style_learning_service()

    def generate_draft_for_email(
        self,
        email: Email,
        target_length: str = "medium",
        target_formality: Optional[str] = None,
        additional_instructions: str = ""
    ) -> Optional[Draft]:
        """
        Generate a draft response for an email with full context.

        Args:
            email: The email to respond to
            target_length: short, medium, or long
            target_formality: casual, professional, formal (or None for auto)
            additional_instructions: Custom instructions

        Returns:
            Draft object or None if generation fails
        """
        logger.info(f"Generating draft for email: {email.subject}")

        try:
            # Get user's style profile
            style_profile = self.db_service.get_active_style_profile()

            # Get or create sender profile
            sender_profile = None
            if email.sender_email:
                sender_profile = self.db_service.get_or_create_sender_profile(
                    email.sender_email,
                    email.sender_name or ""
                )

            # Auto-determine formality if not specified
            if not target_formality:
                if sender_profile and sender_profile.avg_formality_score is not None:
                    # Match sender's usual formality
                    if sender_profile.avg_formality_score > 0.7:
                        target_formality = "formal"
                    elif sender_profile.avg_formality_score > 0.5:
                        target_formality = "professional"
                    else:
                        target_formality = "casual"
                else:
                    target_formality = "professional"  # Default

            # Get email thread context
            thread_context = self._get_thread_context(email)

            # Clean email content
            email_content = clean_email_text(email.body_html, email.body_text)
            email_body = extract_email_body_only(email_content)

            if not email_body:
                logger.error("No email content to respond to")
                return None

            # Generate draft using AI
            result = self.ai_service.generate_draft(
                email_content=email_body,
                email_subject=email.subject or "(No Subject)",
                sender_email=email.sender_email,
                style_profile=style_profile,
                sender_profile=sender_profile,
                thread_context=thread_context,
                target_length=target_length,
                target_formality=target_formality,
                additional_instructions=additional_instructions
            )

            # Create draft object
            draft = Draft(
                original_email_id=email.message_id,
                conversation_id=email.conversation_id,
                draft_version=1,
                subject=f"Re: {email.subject}" if email.subject else "Re: (No Subject)",
                body_content=result["draft"],
                content_type="Text",
                ai_model_used=result["model_used"],
                prompt_used=result["prompt_used"],
                tokens_used=result["tokens_used"],
                target_formality=target_formality,
                target_length=target_length,
                status="generated"
            )

            # Save draft to database
            saved_draft = self.db_service.save_draft(draft)

            logger.info(f"Draft generated successfully (ID: {saved_draft.id})")

            return saved_draft

        except Exception as e:
            logger.exception(f"Failed to generate draft: {e}")
            return None

    def refine_draft(
        self,
        draft: Draft,
        refinement_type: str = "custom",
        custom_instruction: str = ""
    ) -> Optional[Draft]:
        """
        Refine an existing draft.

        Args:
            draft: The draft to refine
            refinement_type: Type of refinement (concise, detailed, formal, casual, etc.)
            custom_instruction: Custom refinement instruction

        Returns:
            New draft version or None
        """
        logger.info(f"Refining draft {draft.id} with type: {refinement_type}")

        try:
            # Get refinement instruction
            if refinement_type == "custom":
                instruction = custom_instruction
            else:
                instruction = REFINEMENT_PRESETS.get(
                    refinement_type,
                    REFINEMENT_PRESETS["grammar"]
                )

            if not instruction:
                logger.error("No refinement instruction provided")
                return None

            # Get style profile
            style_profile = self.db_service.get_active_style_profile()

            # Refine using AI
            result = self.ai_service.refine_draft(
                original_draft=draft.body_content,
                refinement_instruction=instruction,
                style_profile=style_profile
            )

            # Get next version number
            existing_drafts = self.db_service.get_drafts_for_email(draft.original_email_id)
            next_version = max([d.draft_version for d in existing_drafts]) + 1

            # Create new draft version
            refined_draft = Draft(
                original_email_id=draft.original_email_id,
                conversation_id=draft.conversation_id,
                draft_version=next_version,
                parent_draft_id=draft.id,
                subject=draft.subject,
                body_content=result["draft"],
                content_type=draft.content_type,
                ai_model_used=result["model_used"],
                refinement_instruction=instruction,
                tokens_used=result["tokens_used"],
                target_formality=draft.target_formality,
                target_length=draft.target_length,
                status="refined"
            )

            # Save refined draft
            saved_draft = self.db_service.save_draft(refined_draft)

            logger.info(f"Draft refined successfully (ID: {saved_draft.id}, version: {next_version})")

            return saved_draft

        except Exception as e:
            logger.exception(f"Failed to refine draft: {e}")
            return None

    def _get_thread_context(self, email: Email) -> List[str]:
        """Get context from email thread."""
        if not email.conversation_id:
            return []

        try:
            # Get thread emails
            thread_emails = self.db_service.get_email_thread(email.conversation_id)

            # Extract and clean text from thread
            context = []
            for thread_email in thread_emails:
                if thread_email.message_id == email.message_id:
                    continue  # Skip current email

                text = clean_email_text(thread_email.body_html, thread_email.body_text)
                if text:
                    body = extract_email_body_only(text)
                    if body and len(body) > 20:
                        # Add sender info and body
                        sender = thread_email.sender_name or thread_email.sender_email
                        context_text = f"From: {sender}\n{body[:500]}"  # Limit length
                        context.append(context_text)

            logger.debug(f"Found {len(context)} context emails in thread")
            return context

        except Exception as e:
            logger.error(f"Failed to get thread context: {e}")
            return []

    def get_draft_for_email(self, email_id: str) -> Optional[Draft]:
        """Get the latest draft for an email."""
        return self.db_service.get_latest_draft_for_email(email_id)

    def get_all_drafts_for_email(self, email_id: str) -> List[Draft]:
        """Get all draft versions for an email."""
        return self.db_service.get_drafts_for_email(email_id)

    def mark_draft_used(self, draft_id: int, was_edited: bool = False, final_text: str = ""):
        """Mark a draft as used."""
        was_used = 2 if was_edited else 1  # 2 = edited then used, 1 = used as-is
        self.db_service.update_draft_feedback(
            draft_id=draft_id,
            was_used=was_used,
            user_edits=final_text if was_edited else None
        )
        logger.info(f"Draft {draft_id} marked as used (edited: {was_edited})")

    def mark_draft_discarded(self, draft_id: int):
        """Mark a draft as discarded."""
        with self.db_service.get_session() as session:
            draft = session.query(Draft).filter_by(id=draft_id).first()
            if draft:
                draft.status = "discarded"
                session.commit()
        logger.info(f"Draft {draft_id} marked as discarded")


# Global instance
_draft_generator: Optional[DraftGenerator] = None


def get_draft_generator() -> DraftGenerator:
    """Get or create the global DraftGenerator instance."""
    global _draft_generator
    if _draft_generator is None:
        _draft_generator = DraftGenerator()
    return _draft_generator
