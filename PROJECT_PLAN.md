# Email Drafting & Refinement Tool - Project Plan

## Executive Summary

A standalone desktop application that integrates with Microsoft Outlook via Graph API to automatically draft email responses based on your personal writing style, with intelligent refinement capabilities and sender-specific context awareness.

---

## 1. Project Overview

### Core Capabilities
1. **Automatic Draft Generation**: Read latest emails and generate contextual draft responses
2. **Style Learning**: Analyze your sent emails to learn and replicate your writing style
3. **Sender-Specific Adaptation**: Track communication patterns with individual senders across email threads
4. **Iterative Refinement**: Rewrite and expand drafts with a single click
5. **Desktop Integration**: System tray app with hotkey support for quick access
6. **Web Dashboard**: Optional browser-based interface for remote access

### Key Differentiators
- No Outlook add-on required (standalone application)
- Learns from your actual sent emails over time
- Sender-specific context and tone matching
- Corporate email best practices built-in
- Privacy-first: All processing happens locally (except AI API calls)

---

## 2. Technology Stack

### Core Technologies
- **Language**: Python 3.11+
- **Microsoft Integration**: Microsoft Graph API (msal + msgraph-sdk-python)
- **Desktop UI**: PyQt6 (modern, cross-platform, system tray support)
- **Web Dashboard**: Flask + React (optional phase)
- **AI Integration**:
  - Primary: Anthropic Claude API (for drafting and refinement)
  - Alternative: OpenAI GPT-4 API
- **Database**: SQLite (local storage for emails, style profiles, sender history)
- **Caching**: Redis or simple file-based cache for API responses

### Supporting Libraries
- `keyring`: Secure credential storage
- `pydantic`: Data validation and settings management
- `python-dotenv`: Configuration management
- `schedule`: Background tasks for email monitoring
- `pynput`: Global hotkey support
- `textblob` or `language-tool-python`: Grammar checking
- `beautifulsoup4`: Email HTML parsing

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Desktop Application                      │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  System Tray   │  │  Main UI     │  │  Hotkey Handler │ │
│  │   Controller   │  │  (PyQt6)     │  │                 │ │
│  └────────┬───────┘  └──────┬───────┘  └────────┬────────┘ │
│           └──────────────────┼──────────────────┘          │
│                              │                               │
│  ┌──────────────────────────┴───────────────────────────┐  │
│  │           Application Core / Orchestrator             │  │
│  └──────────────────────────┬───────────────────────────┘  │
│                              │                               │
│  ┌──────────┬────────────────┼────────────────┬──────────┐ │
│  │          │                │                │          │ │
│  ▼          ▼                ▼                ▼          ▼ │
│ ┌────┐  ┌────┐           ┌────┐           ┌────┐    ┌────┐│
│ │MS  │  │AI  │           │Style│          │Email│   │Cache││
│ │Graph│ │API │           │Learn│          │DB  │   │Mgr  ││
│ │Svc │  │Svc │           │Eng │           │Svc │   │    ││
│ └────┘  └────┘           └────┘           └────┘    └────┘│
└─────────────────────────────────────────────────────────────┘
           │        │                          │
           ▼        ▼                          ▼
     ┌─────────┐ ┌──────────┐        ┌──────────────┐
     │Microsoft│ │Anthropic │        │ Local SQLite │
     │ Graph   │ │  Claude  │        │   Database   │
     │   API   │ │   API    │        │              │
     └─────────┘ └──────────┘        └──────────────┘
```

---

## 4. Core Components

### 4.1 Microsoft Graph Service
**Responsibilities:**
- OAuth 2.0 authentication (device code flow for personal use)
- Fetch latest emails from inbox
- Retrieve email threads and conversation history
- Search sent emails by sender
- Create draft emails in Outlook
- Monitor specific folders for new emails

**Key APIs:**
- `/me/messages` - List emails
- `/me/messages/{id}` - Get specific email
- `/me/messages/{id}/$value` - Get email content
- `/me/mailFolders/{id}/messages` - Folder-specific emails
- `/me/messages/{id}/createReply` - Create draft reply
- `/me/sendMail` - Send email (optional)

### 4.2 AI Service (Claude API)
**Responsibilities:**
- Generate draft responses based on email content and context
- Refine and rewrite drafts with specific instructions
- Learn writing style from historical emails
- Apply grammar and readability improvements
- Adjust tone for different senders

**Prompting Strategy:**
```
System Prompt Components:
1. Base personality/writing style profile
2. Sender-specific context and history
3. Corporate email best practices
4. Current email thread context
5. Specific refinement instructions (if rewriting)
```

### 4.3 Style Learning Engine
**Responsibilities:**
- Analyze sent emails to extract writing patterns
- Identify common phrases, sign-offs, greetings
- Detect formality levels with different contacts
- Build statistical models of:
  - Average email length
  - Sentence structure preferences
  - Vocabulary choices
  - Paragraph organization
  - Use of bullet points, numbered lists
  - Sign-off preferences

**Data Points to Track:**
- Average words per email by sender category
- Formality score (casual vs. professional)
- Response time patterns
- Emoji usage (if any)
- Greeting variations
- Closing variations
- Common phrases/templates

### 4.4 Email Database Service
**SQLite Schema:**

```sql
-- User's sent emails for style learning
CREATE TABLE sent_emails (
    id INTEGER PRIMARY KEY,
    message_id TEXT UNIQUE,
    sender_email TEXT,
    recipient_emails TEXT,  -- JSON array
    subject TEXT,
    body_text TEXT,
    body_html TEXT,
    sent_datetime TIMESTAMP,
    thread_id TEXT,
    in_reply_to TEXT,
    metadata JSON,  -- Additional Graph API metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sender-specific communication profiles
CREATE TABLE sender_profiles (
    id INTEGER PRIMARY KEY,
    sender_email TEXT UNIQUE,
    sender_name TEXT,
    total_emails_sent INTEGER DEFAULT 0,
    total_emails_received INTEGER DEFAULT 0,
    avg_formality_score REAL,
    common_topics TEXT,  -- JSON array
    preferred_greeting TEXT,
    preferred_signoff TEXT,
    avg_response_length INTEGER,
    last_interaction TIMESTAMP,
    style_notes TEXT,  -- JSON with learned patterns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Draft history and refinements
CREATE TABLE draft_history (
    id INTEGER PRIMARY KEY,
    original_email_id TEXT,
    draft_version INTEGER,
    draft_content TEXT,
    refinement_instruction TEXT,
    ai_model_used TEXT,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application settings and style profile
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_sent_emails_sender ON sent_emails(sender_email);
CREATE INDEX idx_sent_emails_thread ON sent_emails(thread_id);
CREATE INDEX idx_sender_profiles_email ON sender_profiles(sender_email);
```

### 4.5 Desktop UI (PyQt6)
**Main Window Components:**

1. **Email List View**
   - Display recent unread emails
   - Show sender, subject, preview
   - Color coding for priority/categories
   - Search and filter capabilities

2. **Email Detail Pane**
   - Full email content display
   - Thread view (conversation history)
   - Sender profile summary

3. **Draft Editor**
   - Rich text editor for draft response
   - "Generate Draft" button
   - "Refine Draft" button with options:
     - Make more concise
     - Make more detailed
     - Make more formal
     - Make more casual
     - Fix grammar only
     - Custom instruction
   - "Copy to Outlook" button
   - "Send Directly" button (optional)

4. **System Tray**
   - Quick access icon
   - Context menu:
     - Show/Hide main window
     - Check for new emails
     - Generate draft for latest email
     - Settings
     - Exit

5. **Settings Panel**
   - Microsoft account connection status
   - AI API configuration (key, model selection)
   - Hotkey customization
   - Style learning preferences
   - Auto-fetch interval
   - Theme selection (light/dark)

**Hotkey Bindings (Configurable):**
- `Ctrl+Alt+E`: Show main window
- `Ctrl+Alt+D`: Generate draft for selected email
- `Ctrl+Alt+R`: Refine current draft
- `Ctrl+Alt+C`: Copy draft to clipboard

---

## 5. Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Deliverables:**
- [ ] Project structure and development environment
- [ ] Microsoft Graph API authentication (OAuth device flow)
- [ ] Basic email fetching (latest N emails)
- [ ] SQLite database setup with schema
- [ ] Configuration management (.env, settings)

**Files to Create:**
```
emailv2/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Configuration management
│   ├── services/
│   │   ├── __init__.py
│   │   ├── graph_service.py       # Microsoft Graph API
│   │   ├── ai_service.py          # Claude API integration
│   │   ├── db_service.py          # Database operations
│   │   └── cache_service.py       # Caching layer
│   ├── models/
│   │   ├── __init__.py
│   │   ├── email.py               # Email data models
│   │   ├── sender_profile.py      # Sender profile models
│   │   └── draft.py               # Draft models
│   └── utils/
│       ├── __init__.py
│       ├── auth.py                # Authentication helpers
│       └── text_processing.py     # Text utilities
├── tests/
│   └── __init__.py
├── .env.example
├── requirements.txt
├── README.md
└── setup.py
```

### Phase 2: AI Integration & Style Learning (Week 2-3)
**Deliverables:**
- [ ] Claude API integration for draft generation
- [ ] Historical email analysis (fetch sent emails)
- [ ] Style profile builder
- [ ] Sender-specific profile creation
- [ ] Basic prompt engineering for drafts

**Key Features:**
- Fetch last 200-500 sent emails for initial style analysis
- Extract writing patterns and common phrases
- Create baseline style profile
- Generate first drafts using learned style

### Phase 3: Desktop UI Development (Week 3-4)
**Deliverables:**
- [ ] PyQt6 main window with email list
- [ ] Email detail view with thread support
- [ ] Draft editor with rich text support
- [ ] System tray integration
- [ ] Hotkey support (global keyboard shortcuts)
- [ ] Basic settings panel

**UI Workflow:**
1. App starts in system tray
2. User clicks tray icon or uses hotkey
3. Main window shows unread emails
4. User selects email
5. Clicks "Generate Draft"
6. Draft appears in editor
7. User can refine, copy, or send

### Phase 4: Draft Refinement & Polish (Week 4-5)
**Deliverables:**
- [ ] Iterative refinement system
- [ ] Grammar and spelling check integration
- [ ] Multiple refinement options (concise, detailed, formal, casual)
- [ ] Custom refinement instructions
- [ ] Draft version history
- [ ] Corporate email best practices integration

**Refinement Options:**
- Grammar & spelling only
- Make more concise (reduce 20-30%)
- Expand with details
- Adjust formality level
- Simplify language
- Add/remove bullet points
- Custom instruction field

### Phase 5: Advanced Features (Week 5-6)
**Deliverables:**
- [ ] Continuous style learning (improve over time)
- [ ] Sender-specific tone adaptation
- [ ] Email thread context awareness
- [ ] Template system for common scenarios
- [ ] Performance optimizations
- [ ] Comprehensive error handling

**Smart Features:**
- Detect email categories (meeting request, question, update, etc.)
- Suggest response urgency based on sender and content
- Auto-save drafts to Outlook
- Batch processing for multiple emails

### Phase 6: Web Dashboard (Optional - Week 6-7)
**Deliverables:**
- [ ] Flask REST API backend
- [ ] React frontend for web interface
- [ ] Email viewing and drafting via web
- [ ] Sync with desktop app
- [ ] Mobile-responsive design

---

## 6. Authentication & Security

### Microsoft OAuth Setup
1. Register app in Azure AD Portal (https://portal.azure.com)
2. Create app registration for personal use
3. Configure permissions:
   - `Mail.Read` - Read user emails
   - `Mail.ReadWrite` - Create drafts
   - `Mail.Send` - Send emails (optional)
   - `User.Read` - Basic profile
4. Use device code flow (best for CLI/desktop apps)
5. Store tokens securely using `keyring` library

### API Keys Security
- Store Claude API key in system keyring
- Never commit keys to version control
- Use environment variables for development
- Implement key rotation support

### Data Privacy
- All email content stored locally in SQLite
- Encrypt sensitive fields in database
- Clear cache option for privacy
- Option to exclude certain senders from style learning

---

## 7. Configuration Files

### .env.example
```env
# Microsoft Graph API
AZURE_CLIENT_ID=your_client_id_here
AZURE_TENANT_ID=common  # or your tenant ID
AZURE_REDIRECT_URI=http://localhost:8000/callback

# AI Service
ANTHROPIC_API_KEY=your_claude_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
# Alternative: OPENAI_API_KEY for GPT-4

# Application Settings
DATABASE_PATH=./data/emailv2.db
CACHE_DIR=./cache
LOG_LEVEL=INFO
AUTO_FETCH_INTERVAL=300  # seconds

# UI Settings
THEME=dark
DEFAULT_HOTKEY_SHOW=ctrl+alt+e
DEFAULT_HOTKEY_DRAFT=ctrl+alt+d
```

### requirements.txt (Initial)
```txt
# Microsoft Graph API
msal>=1.25.0
msgraph-sdk>=1.0.0
azure-identity>=1.15.0

# AI Integration
anthropic>=0.18.0
# openai>=1.0.0  # Alternative

# Desktop UI
PyQt6>=6.6.0
pynput>=1.7.6

# Database & Storage
sqlalchemy>=2.0.0
alembic>=1.13.0  # Database migrations

# Utilities
python-dotenv>=1.0.0
pydantic>=2.5.0
keyring>=24.3.0
requests>=2.31.0

# Text Processing
beautifulsoup4>=4.12.0
lxml>=5.0.0
language-tool-python>=2.8.0  # Grammar checking

# Background Tasks
schedule>=1.2.0

# Optional Web Dashboard
flask>=3.0.0
flask-cors>=4.0.0
```

---

## 8. AI Prompting Strategy

### Base System Prompt Template
```
You are an AI assistant helping to draft professional email responses.

WRITING STYLE PROFILE:
{user_style_profile}

SENDER CONTEXT:
- Sender: {sender_name} ({sender_email})
- Relationship: {relationship_type}
- Previous interactions: {interaction_count}
- Typical formality: {formality_level}
- Common topics: {topics}

SENDER-SPECIFIC PATTERNS:
{sender_specific_patterns}

CURRENT EMAIL THREAD:
{email_thread_context}

INSTRUCTIONS:
1. Write a response that matches the user's typical style
2. Adapt tone for this specific sender based on history
3. Be concise but complete
4. Use professional corporate email best practices
5. {specific_refinement_instructions}

Generate only the email body, no subject line.
```

### Style Profile Format (JSON)
```json
{
  "avg_email_length": 150,
  "formality_score": 0.7,
  "common_greetings": ["Hi", "Hello", "Hey"],
  "common_signoffs": ["Best", "Thanks", "Best regards"],
  "uses_bullets": true,
  "uses_emojis": false,
  "paragraph_style": "short",
  "tone_descriptors": ["professional", "friendly", "direct"],
  "common_phrases": [
    "Let me know if you have any questions",
    "Happy to discuss further",
    "Thanks for reaching out"
  ],
  "sentence_complexity": "moderate",
  "active_vs_passive": "active"
}
```

### Refinement Instructions
```python
REFINEMENT_PROMPTS = {
    "concise": "Rewrite this email to be 30% shorter while keeping key information.",
    "detailed": "Expand this email with more details and context.",
    "formal": "Rewrite this email in a more formal, professional tone.",
    "casual": "Rewrite this email in a more casual, friendly tone.",
    "grammar": "Fix only grammar, spelling, and punctuation errors. Keep everything else the same.",
    "bullets": "Reorganize the main points as bullet points for clarity.",
    "simplify": "Simplify the language to make it easier to understand."
}
```

---

## 9. Corporate Email Best Practices (Built-in)

The AI service will be prompted with these best practices:

1. **Structure**
   - Clear subject line (if generating new email)
   - Greeting appropriate to relationship
   - Brief context (if replying to a thread)
   - Main message (1-3 short paragraphs or bullets)
   - Clear call-to-action or next steps
   - Professional sign-off

2. **Tone Guidelines**
   - Professional but personable
   - Avoid jargon unless industry-appropriate
   - Use active voice
   - Be direct and clear
   - Avoid unnecessary apologies

3. **Formatting**
   - Short paragraphs (2-3 sentences max)
   - Use bullet points for lists
   - Bold or italic for emphasis (sparingly)
   - No walls of text

4. **Content**
   - Answer all questions asked
   - Anticipate follow-up questions
   - Provide context for decisions
   - Include relevant deadlines or timelines
   - Proofread for errors

---

## 10. Success Metrics

### Technical Metrics
- Email fetch latency < 2 seconds
- Draft generation time < 5 seconds
- UI responsiveness (no freezing)
- Database query performance < 100ms
- API error rate < 1%

### User Experience Metrics
- Draft acceptance rate (how often you use the draft as-is)
- Refinement iterations needed (target: 1-2 max)
- Time saved per email (target: 2-3 minutes)
- Style accuracy (subjective feedback)

### Style Learning Metrics
- Number of sent emails analyzed
- Sender profiles created
- Style confidence score
- Improvement over time (tracked via feedback)

---

## 11. Future Enhancements (Post-MVP)

### Phase 7+
1. **Multi-account Support**: Handle multiple email accounts
2. **Smart Scheduling**: Suggest best time to send emails
3. **Follow-up Reminders**: Track emails awaiting responses
4. **Email Analytics**: Insights on communication patterns
5. **Template Library**: Pre-built templates for common scenarios
6. **Voice Input**: Dictate email content
7. **Mobile App**: iOS/Android companion app
8. **Slack Integration**: Draft Slack messages with same style
9. **Meeting Scheduler**: Smart meeting time suggestions
10. **Email Summarization**: Digest multiple emails into summary

---

## 12. Development Timeline

**Total Estimated Time: 6-8 weeks**

| Phase | Duration | Key Milestone |
|-------|----------|---------------|
| Phase 1: Foundation | 1-2 weeks | Auth + Email fetching working |
| Phase 2: AI Integration | 1 week | First draft generation working |
| Phase 3: Desktop UI | 1-2 weeks | Functional desktop app |
| Phase 4: Refinement | 1 week | Polish and refinement features |
| Phase 5: Advanced Features | 1 week | Style learning optimized |
| Phase 6: Web Dashboard | 1-2 weeks | Optional web interface |

---

## 13. Risk Mitigation

### Technical Risks
- **Microsoft API Rate Limits**: Implement caching and request throttling
- **API Cost (Claude)**: Cache responses, use efficient prompts, consider token limits
- **Auth Token Expiry**: Implement automatic token refresh
- **Database Performance**: Use indexes, consider pagination for large datasets

### User Experience Risks
- **Inaccurate Style Learning**: Require minimum 50 emails for initial profile
- **Poor Draft Quality**: Allow easy manual editing and feedback mechanism
- **Slow Performance**: Implement background processing and progress indicators

### Security Risks
- **Token Theft**: Use OS keyring, encrypt sensitive data
- **API Key Exposure**: Never log or display keys
- **Email Privacy**: Clear privacy policy, local-first architecture

---

## 14. Testing Strategy

### Unit Tests
- Microsoft Graph API service methods
- AI service prompt generation
- Database CRUD operations
- Style learning algorithms

### Integration Tests
- End-to-end email fetch → draft generation
- OAuth flow simulation
- Draft creation in Outlook

### User Acceptance Testing
- Generate drafts for various email types
- Test refinement with different instructions
- Verify style learning accuracy
- Test hotkeys and system tray functionality

---

## Next Steps

1. **Review and approve this plan**
2. **Set up Azure AD app registration** (for Microsoft Graph API)
3. **Get Claude API key** (from Anthropic Console)
4. **Begin Phase 1 implementation**

---

## Questions or Modifications?

This plan is designed to be iterative. We can adjust scope, timeline, or technical decisions as we progress. Let me know if you'd like to:
- Change any technology choices
- Adjust the feature set
- Modify the implementation order
- Add/remove any components

---

**Document Version**: 1.0
**Last Updated**: 2025-11-16
**Status**: Draft - Awaiting Approval
