# Implementation Roadmap

Detailed task breakdown for building the Email Drafting & Refinement Tool.

---

## Phase 1: Foundation & Authentication (Week 1-2)

### 1.1 Environment Setup ✓
- [x] Project structure created
- [x] Dependencies defined (requirements.txt)
- [x] Configuration management (config.py)
- [x] Logging setup
- [ ] Virtual environment setup
- [ ] Install dependencies

### 1.2 Microsoft Graph API Integration
- [ ] Implement OAuth device code flow in `src/utils/auth.py`
- [ ] Token storage using system keyring
- [ ] Token refresh mechanism
- [ ] Basic Graph API client in `src/services/graph_service.py`
- [ ] Test authentication with `/me` endpoint
- [ ] Implement error handling and retry logic

### 1.3 Database Setup
- [ ] Define SQLAlchemy models in `src/models/`
  - [ ] `email.py` - Email model
  - [ ] `sender_profile.py` - Sender profile model
  - [ ] `draft.py` - Draft model
  - [ ] `app_settings.py` - Settings model
- [ ] Database initialization in `src/services/db_service.py`
- [ ] Create Alembic migrations
- [ ] Implement CRUD operations
- [ ] Add indexes for performance

### 1.4 Email Fetching
- [ ] Implement `fetch_recent_emails()` in graph_service
- [ ] Implement `fetch_email_by_id()`
- [ ] Implement `fetch_sent_emails()` for style learning
- [ ] Parse email content (HTML to text)
- [ ] Store emails in database
- [ ] Handle pagination for large email volumes

### 1.5 Testing
- [ ] Unit tests for authentication
- [ ] Unit tests for email fetching
- [ ] Unit tests for database operations
- [ ] Integration test: fetch and store emails

**Deliverables:**
- Working Microsoft authentication
- Ability to fetch emails from inbox
- Emails stored in SQLite database
- Basic error handling and logging

---

## Phase 2: AI Integration & Style Learning (Week 2-3)

### 2.1 Claude API Integration
- [ ] Implement `src/services/ai_service.py`
- [ ] Basic Claude API client
- [ ] Prompt template system
- [ ] Response parsing and validation
- [ ] Error handling and rate limiting
- [ ] Token usage tracking

### 2.2 Style Learning Engine
- [ ] Implement `src/utils/text_processing.py`
- [ ] Email text extraction and cleaning
- [ ] Writing style analysis:
  - [ ] Average email length calculation
  - [ ] Formality score detection
  - [ ] Common phrases extraction
  - [ ] Greeting/signoff pattern detection
  - [ ] Sentence structure analysis
- [ ] Build user style profile
- [ ] Store style profile in database

### 2.3 Sender Profile System
- [ ] Analyze email history per sender
- [ ] Detect relationship type (colleague, client, friend)
- [ ] Calculate formality level per sender
- [ ] Track communication patterns
- [ ] Update sender profiles automatically

### 2.4 Draft Generation
- [ ] Implement base draft generation prompt
- [ ] Include user style profile in prompt
- [ ] Include sender context in prompt
- [ ] Include email thread context
- [ ] Generate initial draft response
- [ ] Validate and clean generated draft

### 2.5 Testing
- [ ] Unit tests for AI service
- [ ] Unit tests for style analysis
- [ ] Integration test: analyze sent emails → generate draft
- [ ] Test with various email types

**Deliverables:**
- Working Claude API integration
- Style learning from sent emails
- Sender-specific profiles created
- Basic draft generation working

---

## Phase 3: Desktop UI Development (Week 3-4)

### 3.1 Main Window (PyQt6)
- [ ] Create `src/ui/main_window.py`
- [ ] Application window structure
- [ ] Email list view (QListWidget or QTableView)
- [ ] Email detail pane (QTextBrowser)
- [ ] Draft editor (QTextEdit with rich text)
- [ ] Button panel (Generate, Refine, Copy, Send)
- [ ] Menu bar (File, Edit, View, Settings, Help)
- [ ] Status bar

### 3.2 Email List Component
- [ ] Display email sender, subject, date
- [ ] Unread/read indicators
- [ ] Priority/importance flags
- [ ] Search and filter functionality
- [ ] Sort options (date, sender, subject)
- [ ] Pagination for large lists
- [ ] Auto-refresh on new emails

### 3.3 Email Detail Component
- [ ] Display full email content
- [ ] HTML rendering support
- [ ] Thread/conversation view
- [ ] Attachment indicators
- [ ] Sender profile summary sidebar

### 3.4 Draft Editor Component
- [ ] Rich text editing
- [ ] Formatting toolbar (bold, italic, bullets, etc.)
- [ ] Character/word count
- [ ] Undo/redo support
- [ ] Draft auto-save
- [ ] Version history indicator

### 3.5 System Tray Integration
- [ ] Create `src/ui/system_tray.py`
- [ ] System tray icon
- [ ] Context menu:
  - [ ] Show/Hide window
  - [ ] Check for new emails
  - [ ] Generate draft for latest
  - [ ] Settings
  - [ ] Exit
- [ ] Notification system for new emails
- [ ] Minimize to tray

### 3.6 Hotkey Support
- [ ] Global hotkey listener using pynput
- [ ] Configurable hotkey bindings
- [ ] Hotkey actions:
  - [ ] Show/hide main window
  - [ ] Generate draft
  - [ ] Refine draft
  - [ ] Copy to clipboard

### 3.7 Settings Dialog
- [ ] Create `src/ui/settings_dialog.py`
- [ ] Tabs: General, Accounts, AI, Hotkeys, Privacy
- [ ] Microsoft account status and re-auth
- [ ] AI service configuration
- [ ] Hotkey customization
- [ ] Theme selection (light/dark)
- [ ] Auto-fetch settings
- [ ] Privacy options

### 3.8 Testing
- [ ] UI component tests
- [ ] Integration tests for user workflows
- [ ] Manual testing on different OS

**Deliverables:**
- Fully functional desktop application
- System tray integration working
- Hotkeys configured and working
- Settings panel complete

---

## Phase 4: Draft Refinement & Polish (Week 4-5)

### 4.1 Refinement System
- [ ] Implement refinement prompt templates
- [ ] Refinement options:
  - [ ] Make concise (reduce 20-30%)
  - [ ] Add details (expand)
  - [ ] More formal
  - [ ] More casual
  - [ ] Fix grammar only
  - [ ] Simplify language
  - [ ] Add bullet points
  - [ ] Custom instruction
- [ ] Track refinement history
- [ ] Undo refinement feature

### 4.2 Grammar & Spell Check
- [ ] Integrate language-tool-python
- [ ] Real-time grammar checking
- [ ] Spelling correction
- [ ] Suggestion highlighting in UI
- [ ] One-click fix all

### 4.3 Corporate Email Best Practices
- [ ] Build best practices prompt template
- [ ] Detect email type (request, update, question, etc.)
- [ ] Apply appropriate structure
- [ ] Ensure clear call-to-action
- [ ] Optimize for readability
- [ ] Professional tone enforcement

### 4.4 Draft Versioning
- [ ] Save each draft version
- [ ] Version comparison view
- [ ] Restore previous version
- [ ] Show what changed between versions

### 4.5 Quality Indicators
- [ ] Readability score
- [ ] Formality level indicator
- [ ] Length indicator (too short/long/just right)
- [ ] Tone match indicator (vs. sender history)
- [ ] Grammar score

### 4.6 Testing
- [ ] Test all refinement options
- [ ] Test grammar checking
- [ ] Test version history
- [ ] User acceptance testing

**Deliverables:**
- Multiple refinement options working
- Grammar checking integrated
- Draft versioning system
- Quality indicators displayed

---

## Phase 5: Advanced Features (Week 5-6)

### 5.1 Continuous Style Learning
- [ ] Background job to analyze new sent emails
- [ ] Incremental style profile updates
- [ ] Track style changes over time
- [ ] Adapt to evolving writing patterns

### 5.2 Sender-Specific Adaptation
- [ ] Auto-detect relationship changes
- [ ] Suggest tone adjustments per sender
- [ ] Learn from manual draft edits
- [ ] Build sender-specific phrase library

### 5.3 Thread Context Awareness
- [ ] Fetch full email thread
- [ ] Analyze conversation flow
- [ ] Reference previous points in thread
- [ ] Maintain context consistency

### 5.4 Template System
- [ ] Common email templates:
  - [ ] Meeting request response
  - [ ] Thank you
  - [ ] Follow-up
  - [ ] Out of office
  - [ ] Introduction
- [ ] Custom template creation
- [ ] Template variables/placeholders
- [ ] Template categories

### 5.5 Batch Processing
- [ ] Select multiple emails
- [ ] Generate drafts for all
- [ ] Queue-based processing
- [ ] Progress indicator

### 5.6 Performance Optimization
- [ ] API response caching
- [ ] Database query optimization
- [ ] Lazy loading for large datasets
- [ ] Background processing for non-urgent tasks
- [ ] Memory usage optimization

### 5.7 Error Handling
- [ ] Comprehensive error messages
- [ ] Graceful degradation
- [ ] Offline mode support
- [ ] Retry mechanisms
- [ ] User-friendly error dialogs

### 5.8 Testing
- [ ] Performance benchmarks
- [ ] Load testing
- [ ] Error scenario testing
- [ ] Full integration testing

**Deliverables:**
- Continuous improvement system
- Smart sender adaptation
- Thread-aware drafting
- Template library
- Robust error handling

---

## Phase 6: Web Dashboard (Optional - Week 6-7)

### 6.1 Backend API (Flask)
- [ ] Create `src/web/app.py`
- [ ] REST API endpoints:
  - [ ] GET /api/emails
  - [ ] GET /api/emails/{id}
  - [ ] POST /api/drafts/generate
  - [ ] POST /api/drafts/refine
  - [ ] GET /api/profile/style
  - [ ] GET /api/senders
- [ ] Authentication (JWT)
- [ ] CORS configuration
- [ ] WebSocket for real-time updates

### 6.2 Frontend (React)
- [ ] Create React app in `web/frontend/`
- [ ] Email list view
- [ ] Email detail view
- [ ] Draft editor component
- [ ] Settings page
- [ ] Dashboard/analytics page
- [ ] Responsive design (mobile-friendly)

### 6.3 Desktop-Web Sync
- [ ] Shared database access
- [ ] Real-time sync via WebSocket
- [ ] Conflict resolution
- [ ] Sync status indicators

### 6.4 Deployment
- [ ] Flask app packaging
- [ ] React build optimization
- [ ] Docker containerization (optional)
- [ ] Local server setup guide

### 6.5 Testing
- [ ] API endpoint tests
- [ ] Frontend component tests
- [ ] E2E tests with Cypress/Playwright
- [ ] Mobile responsiveness testing

**Deliverables:**
- Working web dashboard
- Real-time sync with desktop app
- Mobile-accessible interface

---

## Post-MVP Enhancements (Future)

### Analytics & Insights
- [ ] Email response time analytics
- [ ] Communication pattern insights
- [ ] Most frequent senders/topics
- [ ] Draft usage statistics
- [ ] Style evolution over time

### Smart Features
- [ ] Auto-prioritize emails based on sender/content
- [ ] Suggest response urgency
- [ ] Detect action items in emails
- [ ] Smart scheduling for sending emails
- [ ] Follow-up reminders

### Integrations
- [ ] Slack message drafting
- [ ] Teams integration
- [ ] Calendar integration (meeting scheduling)
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] Task management (Todoist, Asana)

### AI Enhancements
- [ ] Multi-language support
- [ ] Voice input for drafting
- [ ] Email summarization
- [ ] Auto-categorization
- [ ] Smart replies (quick responses)

### Mobile App
- [ ] iOS app (Swift/SwiftUI)
- [ ] Android app (Kotlin)
- [ ] Push notifications
- [ ] Mobile-optimized drafting

---

## Current Status

**Current Phase**: Phase 1 - Foundation
**Completed**: Project planning and structure
**Next Up**: Microsoft Graph authentication implementation

---

## Quick Reference

### Priority Order (MVP)
1. **P0 (Critical)**: Authentication, Email fetching, Basic draft generation, Desktop UI
2. **P1 (Important)**: Style learning, Refinement, Sender profiles
3. **P2 (Nice to have)**: Templates, Web dashboard, Advanced analytics

### Time Estimates
- **Minimum Viable Product (MVP)**: 4-5 weeks (Phases 1-4)
- **Full Featured v1.0**: 6-7 weeks (Phases 1-5)
- **With Web Dashboard**: 8-9 weeks (Phases 1-6)

### Success Criteria (MVP)
- [ ] Can authenticate with Microsoft account
- [ ] Can fetch and display emails
- [ ] Can generate contextual draft responses
- [ ] Drafts match user's writing style
- [ ] Can refine drafts with one click
- [ ] Desktop UI is responsive and intuitive
- [ ] Saves 2-3 minutes per email response

---

**Document Version**: 1.0
**Last Updated**: 2025-11-16
**Status**: Active Development
