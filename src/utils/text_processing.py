"""
Text processing utilities for email analysis and style learning.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from bs4 import BeautifulSoup
import html2text

logger = logging.getLogger(__name__)


def clean_email_text(html_content: str, plain_content: str = "") -> str:
    """
    Extract clean text from email content.

    Args:
        html_content: HTML email content
        plain_content: Plain text email content (fallback)

    Returns:
        Clean text content
    """
    if plain_content and plain_content.strip():
        return plain_content.strip()

    if not html_content or not html_content.strip():
        return ""

    try:
        # Use html2text for better formatting
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = False
        text = h.handle(html_content)

        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()

        return text

    except Exception as e:
        logger.warning(f"Failed to parse HTML content: {e}")

        # Fallback: use BeautifulSoup
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            text = soup.get_text(separator='\n')
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()
        except:
            return html_content


def extract_greeting(email_text: str) -> Optional[str]:
    """
    Extract the greeting from an email.

    Args:
        email_text: Email text content

    Returns:
        Greeting string or None
    """
    # Common greeting patterns
    greeting_patterns = [
        r'^(Hi|Hello|Hey|Dear|Good morning|Good afternoon|Good evening)\s+[\w\s,]+[,:]?',
        r'^(Hi|Hello|Hey)\s*[,:]',
        r'^(Dear)\s+[\w\s]+[,:]'
    ]

    lines = email_text.strip().split('\n')
    if not lines:
        return None

    first_line = lines[0].strip()

    for pattern in greeting_patterns:
        match = re.match(pattern, first_line, re.IGNORECASE)
        if match:
            greeting = match.group(0).rstrip(',: ')
            return greeting

    return None


def extract_signoff(email_text: str) -> Optional[str]:
    """
    Extract the sign-off from an email.

    Args:
        email_text: Email text content

    Returns:
        Sign-off string or None
    """
    # Common sign-off patterns
    signoff_patterns = [
        r'(Best regards|Best|Regards|Thanks|Thank you|Sincerely|Cheers|Kind regards|Warm regards)',
        r'(Talk soon|Speak soon|Take care|All the best)',
        r'(Warmly|Cordially|Respectfully)'
    ]

    lines = email_text.strip().split('\n')
    if len(lines) < 2:
        return None

    # Check last 3 lines
    last_lines = lines[-3:]

    for line in reversed(last_lines):
        line = line.strip()
        for pattern in signoff_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                signoff = match.group(0)
                return signoff

    return None


def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(re.findall(r'\b\w+\b', text))


def detect_formality_score(email_text: str) -> float:
    """
    Estimate formality score of email text.

    Returns:
        Float between 0.0 (very casual) and 1.0 (very formal)
    """
    if not email_text:
        return 0.5

    text_lower = email_text.lower()
    score = 0.5  # Start neutral

    # Formal indicators (increase score)
    formal_phrases = [
        'dear sir', 'dear madam', 'to whom it may concern',
        'i am writing to', 'i would like to', 'please find attached',
        'kindly', 'pursuant to', 'hereby', 'aforementioned',
        'sincerely', 'respectfully', 'yours faithfully'
    ]
    formal_count = sum(1 for phrase in formal_phrases if phrase in text_lower)
    score += min(formal_count * 0.1, 0.3)

    # Casual indicators (decrease score)
    casual_phrases = [
        "hey", "hi there", "what's up", "thanks a bunch",
        "no worries", "sounds good", "cool", "awesome",
        "yeah", "nah", "gonna", "wanna", "gotta"
    ]
    casual_count = sum(1 for phrase in casual_phrases if phrase in text_lower)
    score -= min(casual_count * 0.1, 0.3)

    # Check for contractions (casual)
    contractions = re.findall(r"\w+'\w+", email_text)
    if len(contractions) > 2:
        score -= 0.1

    # Check for exclamation marks (casual)
    exclamation_count = email_text.count('!')
    if exclamation_count > 2:
        score -= 0.1

    # Ensure score is in valid range
    return max(0.0, min(1.0, score))


def extract_phrases(email_text: str, min_frequency: int = 2) -> List[str]:
    """
    Extract common phrases from email text.

    Args:
        email_text: Email text content
        min_frequency: Minimum frequency to consider

    Returns:
        List of common phrases
    """
    if not email_text:
        return []

    # Extract 2-4 word phrases
    words = re.findall(r'\b\w+\b', email_text.lower())

    phrases = []

    # Bigrams (2 words)
    for i in range(len(words) - 1):
        phrase = f"{words[i]} {words[i+1]}"
        phrases.append(phrase)

    # Trigrams (3 words)
    for i in range(len(words) - 2):
        phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
        phrases.append(phrase)

    # Count frequencies
    phrase_counts = Counter(phrases)

    # Filter by frequency and remove very common/generic phrases
    common_phrases = []
    stopwords = {'i am', 'you are', 'it is', 'this is', 'that is', 'to be', 'of the', 'in the', 'for the'}

    for phrase, count in phrase_counts.most_common(20):
        if count >= min_frequency and phrase not in stopwords:
            common_phrases.append(phrase)

    return common_phrases[:10]  # Top 10


def detect_bullet_points(email_text: str) -> bool:
    """Check if email uses bullet points."""
    if not email_text:
        return False

    # Check for common bullet point markers
    bullet_patterns = [
        r'^\s*[-*•]\s+',  # -, *, •
        r'^\s*\d+[\.)]\s+',  # 1. or 1)
        r'^\s*[a-z][\.)]\s+'  # a. or a)
    ]

    lines = email_text.split('\n')

    bullet_count = 0
    for line in lines:
        for pattern in bullet_patterns:
            if re.match(pattern, line):
                bullet_count += 1
                break

    return bullet_count >= 2


def detect_emojis(text: str) -> bool:
    """Check if text contains emojis."""
    if not text:
        return False

    # Simple emoji detection (basic emoji ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "]+",
        flags=re.UNICODE
    )

    return bool(emoji_pattern.search(text))


def analyze_paragraph_style(email_text: str) -> str:
    """
    Analyze paragraph style (short, medium, long).

    Returns:
        "short", "medium", or "long"
    """
    if not email_text:
        return "medium"

    paragraphs = [p.strip() for p in email_text.split('\n\n') if p.strip()]

    if not paragraphs:
        return "short"

    avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)

    if avg_para_length < 30:
        return "short"
    elif avg_para_length < 60:
        return "medium"
    else:
        return "long"


def extract_email_body_only(email_text: str) -> str:
    """
    Extract only the email body, removing quoted text and signatures.

    Args:
        email_text: Full email text

    Returns:
        Clean email body
    """
    if not email_text:
        return ""

    lines = email_text.split('\n')
    body_lines = []

    # Patterns that indicate quoted text or signatures
    quote_patterns = [
        r'^>',  # Quoted with >
        r'^On .+ wrote:',  # Email client quote
        r'^From:',  # Forwarded email
        r'^-{3,}',  # Separator lines
        r'^_{3,}',  # Separator lines
    ]

    signature_indicators = [
        'sent from my',
        'get outlook for',
        'confidentiality notice',
        'disclaimer'
    ]

    in_quote = False

    for line in lines:
        line_lower = line.lower().strip()

        # Check if entering quoted section
        for pattern in quote_patterns:
            if re.match(pattern, line):
                in_quote = True
                break

        # Check for signature indicators
        is_signature = any(indicator in line_lower for indicator in signature_indicators)

        if in_quote or is_signature:
            break

        body_lines.append(line)

    return '\n'.join(body_lines).strip()


def calculate_style_metrics(emails: List[str]) -> Dict[str, Any]:
    """
    Calculate aggregate style metrics from multiple emails.

    Args:
        emails: List of email text contents

    Returns:
        Dict with style metrics
    """
    if not emails:
        return {}

    logger.info(f"Calculating style metrics from {len(emails)} emails")

    greetings = []
    signoffs = []
    word_counts = []
    formality_scores = []
    all_phrases = []
    uses_bullets_count = 0
    uses_emojis_count = 0
    paragraph_styles = []

    for email_text in emails:
        # Clean the email
        email_body = extract_email_body_only(email_text)

        if not email_body or len(email_body) < 20:
            continue

        # Extract greeting
        greeting = extract_greeting(email_body)
        if greeting:
            greetings.append(greeting)

        # Extract signoff
        signoff = extract_signoff(email_body)
        if signoff:
            signoffs.append(signoff)

        # Word count
        word_count = count_words(email_body)
        if word_count > 0:
            word_counts.append(word_count)

        # Formality score
        formality = detect_formality_score(email_body)
        formality_scores.append(formality)

        # Phrases
        phrases = extract_phrases(email_body)
        all_phrases.extend(phrases)

        # Bullet points
        if detect_bullet_points(email_body):
            uses_bullets_count += 1

        # Emojis
        if detect_emojis(email_body):
            uses_emojis_count += 1

        # Paragraph style
        para_style = analyze_paragraph_style(email_body)
        paragraph_styles.append(para_style)

    # Aggregate metrics
    metrics = {
        "avg_word_count": int(sum(word_counts) / len(word_counts)) if word_counts else 0,
        "avg_formality_score": round(sum(formality_scores) / len(formality_scores), 2) if formality_scores else 0.5,
        "common_greetings": [g for g, _ in Counter(greetings).most_common(5)],
        "common_signoffs": [s for s, _ in Counter(signoffs).most_common(5)],
        "common_phrases": [p for p, _ in Counter(all_phrases).most_common(10)],
        "uses_bullets_frequency": round(uses_bullets_count / len(emails), 2) if emails else 0,
        "uses_emojis_frequency": round(uses_emojis_count / len(emails), 2) if emails else 0,
        "most_common_paragraph_style": Counter(paragraph_styles).most_common(1)[0][0] if paragraph_styles else "medium",
        "total_emails_analyzed": len(emails)
    }

    logger.info(f"Style metrics calculated: avg_words={metrics['avg_word_count']}, formality={metrics['avg_formality_score']}")

    return metrics
