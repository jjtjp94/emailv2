"""
AI service for draft generation and refinement using Claude API.
Handles prompt construction, API calls, and response processing.
"""

import logging
from typing import Optional, Dict, Any, List
import json

import anthropic

from src.config import get_settings
from src.models.sender_profile import SenderProfile
from src.models.draft import StyleProfile

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered email drafting and refinement."""

    def __init__(self):
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.ANTHROPIC_API_KEY)
        self.model = self.settings.ANTHROPIC_MODEL

    def generate_draft(
        self,
        email_content: str,
        email_subject: str,
        sender_email: str,
        style_profile: Optional[StyleProfile] = None,
        sender_profile: Optional[SenderProfile] = None,
        thread_context: Optional[List[str]] = None,
        target_length: str = "medium",
        target_formality: str = "professional",
        additional_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a draft email response.

        Args:
            email_content: The email content to respond to
            email_subject: The email subject
            sender_email: Sender's email address
            style_profile: User's writing style profile
            sender_profile: Sender-specific communication profile
            thread_context: Previous emails in the thread
            target_length: short, medium, or long
            target_formality: casual, professional, or formal
            additional_instructions: Custom instructions for the draft

        Returns:
            Dict with 'draft', 'tokens_used', and 'model_used'
        """
        logger.info(f"Generating draft for email from {sender_email}")

        # Build the prompt
        system_prompt = self._build_system_prompt(
            style_profile=style_profile,
            sender_profile=sender_profile,
            target_length=target_length,
            target_formality=target_formality
        )

        user_prompt = self._build_user_prompt(
            email_content=email_content,
            email_subject=email_subject,
            sender_email=sender_email,
            thread_context=thread_context,
            additional_instructions=additional_instructions
        )

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Extract draft content
            draft_content = response.content[0].text

            # Get token usage
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            logger.info(f"Generated draft ({tokens_used} tokens used)")

            return {
                "draft": draft_content,
                "tokens_used": tokens_used,
                "model_used": self.model,
                "prompt_used": user_prompt,
                "system_prompt": system_prompt
            }

        except Exception as e:
            logger.error(f"Failed to generate draft: {e}")
            raise

    def refine_draft(
        self,
        original_draft: str,
        refinement_instruction: str,
        style_profile: Optional[StyleProfile] = None
    ) -> Dict[str, Any]:
        """
        Refine an existing draft based on instructions.

        Args:
            original_draft: The draft to refine
            refinement_instruction: How to refine it
            style_profile: User's writing style profile

        Returns:
            Dict with 'draft', 'tokens_used', and 'model_used'
        """
        logger.info(f"Refining draft with instruction: {refinement_instruction}")

        system_prompt = "You are an expert email editor. Refine the given email draft according to the user's instructions while maintaining professionalism and clarity."

        if style_profile and style_profile.style_summary:
            system_prompt += f"\n\nUser's typical writing style: {style_profile.style_summary}"

        user_prompt = f"""Original email draft:
---
{original_draft}
---

Refinement instructions: {refinement_instruction}

Please provide the refined version of the email. Output ONLY the refined email text, no explanations or commentary."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            refined_draft = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            logger.info(f"Refined draft ({tokens_used} tokens used)")

            return {
                "draft": refined_draft,
                "tokens_used": tokens_used,
                "model_used": self.model,
                "refinement_applied": refinement_instruction
            }

        except Exception as e:
            logger.error(f"Failed to refine draft: {e}")
            raise

    def _build_system_prompt(
        self,
        style_profile: Optional[StyleProfile],
        sender_profile: Optional[SenderProfile],
        target_length: str,
        target_formality: str
    ) -> str:
        """Build the system prompt for draft generation."""

        prompt_parts = [
            "You are an AI assistant helping to draft professional email responses.",
            "Your goal is to write clear, effective, and contextually appropriate email replies."
        ]

        # Add style profile if available
        if style_profile:
            prompt_parts.append("\n## USER'S WRITING STYLE:")

            if style_profile.style_summary:
                prompt_parts.append(style_profile.style_summary)

            if style_profile.avg_email_length:
                prompt_parts.append(f"- Typical email length: {style_profile.avg_email_length} words")

            if style_profile.common_greetings:
                greetings = style_profile.common_greetings
                if isinstance(greetings, list) and len(greetings) > 0:
                    prompt_parts.append(f"- Common greetings: {', '.join(greetings[:3])}")

            if style_profile.common_signoffs:
                signoffs = style_profile.common_signoffs
                if isinstance(signoffs, list) and len(signoffs) > 0:
                    prompt_parts.append(f"- Common sign-offs: {', '.join(signoffs[:3])}")

            if style_profile.tone_descriptors:
                tones = style_profile.tone_descriptors
                if isinstance(tones, list):
                    prompt_parts.append(f"- Writing tone: {', '.join(tones)}")

        # Add sender profile if available
        if sender_profile:
            prompt_parts.append("\n## SENDER CONTEXT:")
            prompt_parts.append(f"- Sender: {sender_profile.sender_name or sender_profile.sender_email}")

            if sender_profile.relationship_type:
                prompt_parts.append(f"- Relationship: {sender_profile.relationship_type}")

            if sender_profile.total_emails_received:
                prompt_parts.append(f"- Previous interactions: {sender_profile.total_emails_received} emails received")

            if sender_profile.avg_formality_score is not None:
                formality_desc = sender_profile.get_formality_description()
                prompt_parts.append(f"- Typical formality with this sender: {formality_desc}")

            if sender_profile.preferred_greeting:
                prompt_parts.append(f"- You typically greet them with: {sender_profile.preferred_greeting}")

            if sender_profile.preferred_signoff:
                prompt_parts.append(f"- You typically sign off with: {sender_profile.preferred_signoff}")

        # Add target parameters
        prompt_parts.append("\n## DRAFT REQUIREMENTS:")

        length_guidance = {
            "short": "Keep the response brief and concise (50-100 words). Get straight to the point.",
            "medium": "Write a moderate-length response (100-200 words). Balance detail with conciseness.",
            "long": "Provide a detailed response (200-300 words). Include thorough explanations."
        }
        prompt_parts.append(f"- Length: {length_guidance.get(target_length, length_guidance['medium'])}")

        formality_guidance = {
            "casual": "Use a friendly, casual tone. Contractions and informal language are fine.",
            "professional": "Use a professional but approachable tone. Polite and clear.",
            "formal": "Use formal business language. Avoid contractions and casual phrases."
        }
        prompt_parts.append(f"- Formality: {formality_guidance.get(target_formality, formality_guidance['professional'])}")

        # Add corporate best practices
        if self.settings.CORPORATE_BEST_PRACTICES:
            prompt_parts.append("\n## EMAIL BEST PRACTICES:")
            prompt_parts.append("- Start with an appropriate greeting")
            prompt_parts.append("- Address all questions and points from the original email")
            prompt_parts.append("- Be clear and direct in your communication")
            prompt_parts.append("- Use short paragraphs (2-3 sentences max)")
            prompt_parts.append("- Include a clear call-to-action if needed")
            prompt_parts.append("- End with an appropriate sign-off")
            prompt_parts.append("- Proofread for grammar and clarity")

        prompt_parts.append("\n## OUTPUT FORMAT:")
        prompt_parts.append("Provide ONLY the email body text. Do not include:")
        prompt_parts.append("- Subject line")
        prompt_parts.append("- Sender/recipient information")
        prompt_parts.append("- Explanations or commentary")
        prompt_parts.append("- Meta-text about the email")

        return "\n".join(prompt_parts)

    def _build_user_prompt(
        self,
        email_content: str,
        email_subject: str,
        sender_email: str,
        thread_context: Optional[List[str]],
        additional_instructions: str
    ) -> str:
        """Build the user prompt with email context."""

        prompt_parts = []

        # Add thread context if available
        if thread_context and len(thread_context) > 0:
            prompt_parts.append("## EMAIL THREAD HISTORY:")
            for i, context_email in enumerate(thread_context[-3:], 1):  # Last 3 emails
                prompt_parts.append(f"\n### Email {i}:")
                prompt_parts.append(context_email[:500])  # Limit length
            prompt_parts.append("")

        # Add current email
        prompt_parts.append("## EMAIL TO RESPOND TO:")
        prompt_parts.append(f"Subject: {email_subject}")
        prompt_parts.append(f"From: {sender_email}")
        prompt_parts.append("\nContent:")
        prompt_parts.append(email_content)

        # Add custom instructions
        if additional_instructions:
            prompt_parts.append(f"\n## ADDITIONAL INSTRUCTIONS:")
            prompt_parts.append(additional_instructions)

        prompt_parts.append("\n## YOUR TASK:")
        prompt_parts.append("Draft a response to this email that:")
        prompt_parts.append("1. Addresses all points raised")
        prompt_parts.append("2. Matches the specified writing style")
        prompt_parts.append("3. Is appropriate for the sender relationship")
        prompt_parts.append("4. Follows email best practices")
        prompt_parts.append("\nProvide only the email body (greeting to sign-off). Begin your response now:")

        return "\n".join(prompt_parts)

    def analyze_email_style(self, email_text: str) -> Dict[str, Any]:
        """
        Analyze the writing style of an email.

        Args:
            email_text: The email text to analyze

        Returns:
            Dict with style metrics
        """
        logger.info("Analyzing email writing style")

        prompt = f"""Analyze the writing style of this email and provide metrics.

Email text:
---
{email_text}
---

Provide analysis in JSON format with these fields:
- formality_score: 0.0 (very casual) to 1.0 (very formal)
- tone: array of descriptors (e.g., ["professional", "friendly", "direct"])
- word_count: number of words
- uses_bullets: boolean
- uses_emojis: boolean
- greeting: the greeting used (if any)
- signoff: the sign-off used (if any)
- key_phrases: array of notable phrases or expressions

Output only valid JSON, no other text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse JSON response
            analysis_text = response.content[0].text

            # Extract JSON if wrapped in markdown
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()

            analysis = json.loads(analysis_text)

            logger.info("Email style analysis complete")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze email style: {e}")
            # Return default values on error
            return {
                "formality_score": 0.5,
                "tone": ["professional"],
                "word_count": len(email_text.split()),
                "uses_bullets": False,
                "uses_emojis": False
            }


# Global instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create the global AIService instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# Predefined refinement instructions
REFINEMENT_PRESETS = {
    "concise": "Make this email more concise by reducing it by 30-40% while keeping all essential information.",
    "detailed": "Expand this email with more details, context, and explanations.",
    "formal": "Rewrite this email in a more formal, professional tone suitable for senior executives.",
    "casual": "Rewrite this email in a more casual, friendly tone while remaining professional.",
    "grammar": "Fix only grammar, spelling, and punctuation errors. Keep everything else exactly the same.",
    "bullets": "Reorganize the main points as bullet points for better clarity and readability.",
    "simplify": "Simplify the language to make it easier to understand. Use shorter words and sentences.",
    "polite": "Make this email more polite and courteous without being overly formal.",
    "direct": "Make this email more direct and to-the-point. Remove unnecessary pleasantries."
}
