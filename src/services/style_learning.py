"""
Style learning service for analyzing user's writing patterns.
Builds and updates user style profile and sender-specific profiles.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter

from src.services.db_service import get_db_service
from src.services.ai_service import get_ai_service
from src.models.email import Email
from src.models.sender_profile import SenderProfile
from src.models.draft import StyleProfile
from src.utils.text_processing import (
    clean_email_text,
    extract_email_body_only,
    calculate_style_metrics,
    extract_greeting,
    extract_signoff,
    count_words,
    detect_formality_score
)

logger = logging.getLogger(__name__)


class StyleLearningService:
    """Service for learning and maintaining user's writing style."""

    def __init__(self):
        self.db_service = get_db_service()
        self.ai_service = get_ai_service()

    def analyze_sent_emails(self, max_emails: int = 200) -> StyleProfile:
        """
        Analyze sent emails to build user's writing style profile.

        Args:
            max_emails: Maximum number of sent emails to analyze

        Returns:
            Updated StyleProfile
        """
        logger.info(f"Starting style analysis of up to {max_emails} sent emails")

        # Get sent emails from database
        sent_emails = self.db_service.get_sent_emails_for_analysis(limit=max_emails)

        if not sent_emails:
            logger.warning("No sent emails found for analysis")
            return self._get_or_create_default_profile()

        logger.info(f"Analyzing {len(sent_emails)} sent emails")

        # Extract email bodies
        email_texts = []
        for email in sent_emails:
            text = clean_email_text(email.body_html, email.body_text)
            if text:
                body = extract_email_body_only(text)
                if body and len(body) > 20:  # Skip very short emails
                    email_texts.append(body)

        if not email_texts:
            logger.warning("No valid email text found")
            return self._get_or_create_default_profile()

        # Calculate style metrics
        metrics = calculate_style_metrics(email_texts)

        # Generate AI summary of writing style
        style_summary = self._generate_style_summary(email_texts[:10])  # Use first 10 emails for summary

        # Update or create style profile
        profile = self.db_service.get_active_style_profile()

        if not profile:
            profile = StyleProfile(
                profile_name="default",
                is_active=1
            )

        # Update profile with metrics
        profile.total_emails_analyzed = len(email_texts)
        profile.last_analysis_date = datetime.utcnow()
        profile.avg_email_length = metrics.get("avg_word_count", 0)
        profile.avg_formality_score = metrics.get("avg_formality_score", 0.5)
        profile.common_greetings = metrics.get("common_greetings", [])
        profile.common_signoffs = metrics.get("common_signoffs", [])
        profile.common_phrases = metrics.get("common_phrases", [])
        profile.paragraph_style = metrics.get("most_common_paragraph_style", "medium")
        profile.style_summary = style_summary

        # Determine bullet point usage
        bullet_freq = metrics.get("uses_bullets_frequency", 0)
        if bullet_freq > 0.3:
            profile.uses_bullet_points = 2  # often
        elif bullet_freq > 0.1:
            profile.uses_bullet_points = 1  # sometimes
        else:
            profile.uses_bullet_points = 0  # rarely

        # Determine emoji usage
        emoji_freq = metrics.get("uses_emojis_frequency", 0)
        if emoji_freq > 0.2:
            profile.uses_emojis = 2
        elif emoji_freq > 0.05:
            profile.uses_emojis = 1
        else:
            profile.uses_emojis = 0

        # Determine tone descriptors
        formality = profile.avg_formality_score
        tone_descriptors = []

        if formality < 0.3:
            tone_descriptors.append("casual")
            tone_descriptors.append("friendly")
        elif formality < 0.5:
            tone_descriptors.append("approachable")
            tone_descriptors.append("professional")
        elif formality < 0.7:
            tone_descriptors.append("professional")
            tone_descriptors.append("polished")
        else:
            tone_descriptors.append("formal")
            tone_descriptors.append("businesslike")

        if profile.avg_email_length < 100:
            tone_descriptors.append("concise")
        elif profile.avg_email_length > 200:
            tone_descriptors.append("detailed")

        profile.tone_descriptors = tone_descriptors

        # Save updated profile
        updated_profile = self.db_service.update_style_profile(
            total_emails_analyzed=profile.total_emails_analyzed,
            last_analysis_date=profile.last_analysis_date,
            avg_email_length=profile.avg_email_length,
            avg_formality_score=profile.avg_formality_score,
            common_greetings=profile.common_greetings,
            common_signoffs=profile.common_signoffs,
            common_phrases=profile.common_phrases,
            uses_bullet_points=profile.uses_bullet_points,
            uses_emojis=profile.uses_emojis,
            paragraph_style=profile.paragraph_style,
            tone_descriptors=profile.tone_descriptors,
            style_summary=profile.style_summary
        )

        logger.info(f"Style profile updated: {profile.total_emails_analyzed} emails analyzed")

        return updated_profile or profile

    def _generate_style_summary(self, sample_emails: List[str]) -> str:
        """Generate AI summary of writing style from sample emails."""
        if not sample_emails:
            return "Professional email style"

        logger.info("Generating AI summary of writing style")

        # Combine sample emails (limit total length)
        combined_text = "\n\n---\n\n".join(sample_emails[:5])
        if len(combined_text) > 3000:
            combined_text = combined_text[:3000] + "..."

        prompt = f"""Analyze these email samples and provide a brief summary of the writing style.

Sample emails:
{combined_text}

Provide a 2-3 sentence summary describing:
- Overall tone and formality level
- Communication style (concise/detailed, direct/diplomatic, etc.)
- Notable patterns or characteristics

Keep it concise and actionable for generating similar emails."""

        try:
            response = self.ai_service.client.messages.create(
                model=self.ai_service.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            summary = response.content[0].text.strip()
            logger.info("Style summary generated successfully")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate style summary: {e}")
            return "Professional and clear email communication style"

    def build_sender_profiles(self, min_emails_per_sender: int = 3):
        """
        Build or update sender-specific communication profiles.

        Args:
            min_emails_per_sender: Minimum emails to create a profile
        """
        logger.info("Building sender profiles")

        # Get all sent emails grouped by recipient
        with self.db_service.get_session() as session:
            sent_emails = session.query(Email).filter_by(email_type="sent").all()

        if not sent_emails:
            logger.warning("No sent emails found for sender profiling")
            return

        # Group emails by recipient
        emails_by_sender: Dict[str, List[Email]] = {}

        for email in sent_emails:
            if not email.to_recipients:
                continue

            # Get first recipient
            recipients = email.to_recipients
            if isinstance(recipients, list) and len(recipients) > 0:
                recipient_email = recipients[0].get("email", "")
                if recipient_email:
                    if recipient_email not in emails_by_sender:
                        emails_by_sender[recipient_email] = []
                    emails_by_sender[recipient_email].append(email)

        logger.info(f"Found emails to {len(emails_by_sender)} unique recipients")

        # Build profile for each sender
        profiles_created = 0
        profiles_updated = 0

        for sender_email, email_list in emails_by_sender.items():
            if len(email_list) < min_emails_per_sender:
                continue

            try:
                profile = self._build_sender_profile(sender_email, email_list)
                if profile:
                    if profile.total_emails_sent == len(email_list):
                        profiles_created += 1
                    else:
                        profiles_updated += 1
            except Exception as e:
                logger.error(f"Failed to build profile for {sender_email}: {e}")

        logger.info(f"Sender profiling complete: {profiles_created} created, {profiles_updated} updated")

    def _build_sender_profile(
        self,
        sender_email: str,
        emails_to_sender: List[Email]
    ) -> Optional[SenderProfile]:
        """Build or update profile for a specific sender."""

        if not emails_to_sender:
            return None

        logger.debug(f"Building profile for {sender_email} ({len(emails_to_sender)} emails)")

        # Get sender name from most recent email
        sender_name = ""
        if emails_to_sender[0].to_recipients:
            sender_name = emails_to_sender[0].to_recipients[0].get("name", "")

        # Get or create profile
        profile = self.db_service.get_or_create_sender_profile(sender_email, sender_name)

        # Extract email texts
        email_texts = []
        greetings = []
        signoffs = []
        word_counts = []
        formality_scores = []

        for email in emails_to_sender:
            text = clean_email_text(email.body_html, email.body_text)
            if not text:
                continue

            body = extract_email_body_only(text)
            if not body or len(body) < 20:
                continue

            email_texts.append(body)

            # Extract greeting
            greeting = extract_greeting(body)
            if greeting:
                greetings.append(greeting)

            # Extract signoff
            signoff = extract_signoff(body)
            if signoff:
                signoffs.append(signoff)

            # Word count
            words = count_words(body)
            if words > 0:
                word_counts.append(words)

            # Formality
            formality = detect_formality_score(body)
            formality_scores.append(formality)

        # Calculate statistics
        if word_counts:
            avg_response_length = int(sum(word_counts) / len(word_counts))
        else:
            avg_response_length = 0

        if formality_scores:
            avg_formality = round(sum(formality_scores) / len(formality_scores), 2)
        else:
            avg_formality = 0.5

        # Most common greeting and signoff
        preferred_greeting = Counter(greetings).most_common(1)[0][0] if greetings else None
        preferred_signoff = Counter(signoffs).most_common(1)[0][0] if signoffs else None

        # Get conversation topics (from subjects)
        subjects = [email.subject for email in emails_to_sender if email.subject]
        common_topics = list(set(subjects[:5]))  # Top 5 unique subjects

        # Determine relationship type based on formality and frequency
        total_sent = len(emails_to_sender)
        if avg_formality > 0.7:
            relationship_type = "client" if total_sent < 10 else "executive"
        elif avg_formality > 0.5:
            relationship_type = "colleague"
        else:
            relationship_type = "friend" if total_sent > 20 else "acquaintance"

        # Update profile
        updated_profile = self.db_service.update_sender_profile(
            sender_email=sender_email,
            sender_name=sender_name,
            total_emails_sent=total_sent,
            avg_formality_score=avg_formality,
            avg_response_length=avg_response_length,
            preferred_greeting=preferred_greeting,
            preferred_signoff=preferred_signoff,
            common_topics=common_topics,
            relationship_type=relationship_type,
            last_interaction_date=emails_to_sender[-1].sent_datetime or datetime.utcnow()
        )

        logger.debug(f"Profile updated for {sender_email}: {relationship_type}, formality={avg_formality}")

        return updated_profile

    def _get_or_create_default_profile(self) -> StyleProfile:
        """Get or create a default style profile."""
        profile = self.db_service.get_active_style_profile()

        if not profile:
            profile = StyleProfile(
                profile_name="default",
                is_active=1,
                style_summary="Professional email communication style",
                avg_email_length=150,
                avg_formality_score=0.6,
                tone_descriptors=["professional", "clear"]
            )

        return profile


# Global instance
_style_learning_service: Optional[StyleLearningService] = None


def get_style_learning_service() -> StyleLearningService:
    """Get or create the global StyleLearningService instance."""
    global _style_learning_service
    if _style_learning_service is None:
        _style_learning_service = StyleLearningService()
    return _style_learning_service
