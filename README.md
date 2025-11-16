# Email Drafting & Refinement Tool

A standalone desktop application that integrates with Microsoft Outlook to automatically draft email responses based on your personal writing style.

## Overview

This tool learns from your email history to generate contextual draft responses that match your writing style. It adapts to different senders and allows iterative refinement with a single click.

## Key Features

- **Automatic Draft Generation**: AI-powered drafts based on your writing style
- **Sender-Specific Adaptation**: Different tone for different contacts
- **One-Click Refinement**: Easily expand, condense, or adjust tone
- **Desktop Integration**: System tray app with global hotkeys
- **Privacy-First**: All data stored locally
- **Style Learning**: Improves over time by analyzing your sent emails

## Technology Stack

- **Language**: Python 3.11+
- **Microsoft Integration**: Microsoft Graph API
- **Desktop UI**: PyQt6
- **AI**: Anthropic Claude API
- **Database**: SQLite

## Quick Start

### Prerequisites

1. **Azure AD App Registration**
   - Go to [Azure Portal](https://portal.azure.com)
   - Register a new app for Microsoft Graph API
   - Note your Client ID and Tenant ID

2. **Anthropic API Key**
   - Get your API key from [Anthropic Console](https://console.anthropic.com)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd emailv2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### Configuration

Edit `.env` file with your credentials:
```env
AZURE_CLIENT_ID=your_client_id
AZURE_TENANT_ID=common
ANTHROPIC_API_KEY=your_api_key
```

### First Run - Setup (CLI Mode)

```bash
# Run setup to authenticate and learn your style
python src/main.py
```

This will:
1. Authenticate with your Microsoft account
2. Fetch your emails
3. Analyze your writing style
4. Generate a sample draft

### Launch Desktop UI

```bash
# Start the GUI application
python run_gui.py
```

**See [QUICKSTART.md](QUICKSTART.md) for detailed step-by-step instructions.**

## Usage

### Desktop Application

The GUI provides a comprehensive email drafting interface:

**Main Window:**
- **Left Pane**: Email list (inbox, sent, unread)
- **Middle Pane**: Selected email details
- **Right Pane**: Draft editor with refinement controls

**Workflow:**
1. Select an email from the list
2. Click "🤖 Generate Draft"
3. Review the AI-generated draft
4. Use refinement buttons to adjust:
   - ✂️ Make Concise
   - 📝 Add Details
   - 👔 More Formal
   - 😊 More Casual
   - ✓ Fix Grammar
   - • Add Bullets
5. Copy to clipboard or create draft in Outlook

**Keyboard Shortcuts:**
- `Ctrl+R`: Refresh emails
- `Ctrl+D`: Generate draft
- `Ctrl+C`: Copy draft to clipboard
- `Ctrl+Q`: Quit application

**System Tray:**
- Minimize to tray for background operation
- Right-click tray icon for quick actions
- Auto-refresh emails every 5 minutes

## Project Structure

```
emailv2/
├── src/
│   ├── main.py                  # Application entry point
│   ├── config.py                # Configuration management
│   ├── services/                # Core services
│   │   ├── graph_service.py     # Microsoft Graph API
│   │   ├── ai_service.py        # Claude API integration
│   │   ├── db_service.py        # Database operations
│   │   └── cache_service.py     # Caching layer
│   ├── models/                  # Data models
│   │   ├── email.py
│   │   ├── sender_profile.py
│   │   └── draft.py
│   ├── ui/                      # User interface
│   │   ├── main_window.py
│   │   ├── system_tray.py
│   │   └── settings_dialog.py
│   └── utils/                   # Utilities
│       ├── auth.py
│       └── text_processing.py
├── tests/                       # Unit tests
├── data/                        # Database and cache
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── PROJECT_PLAN.md              # Detailed project plan
└── README.md                    # This file
```

## Development Status

- [x] Phase 1: Foundation & Authentication
- [x] Phase 2: AI Integration & Style Learning
- [x] Phase 3: Desktop UI Development (Current)
- [ ] Phase 4: Advanced Features & Polish
- [ ] Phase 5: Deployment & Distribution

**Current Version**: 0.3.0 (GUI Beta)

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed implementation timeline.

## Contributing

This is a personal project, but suggestions and improvements are welcome.

## Privacy & Security

- All email data is stored locally in SQLite
- API credentials stored securely using OS keyring
- No data sent to third parties except Microsoft Graph API and Claude API
- Clear cache and data options available in settings

## Screenshots

### Main Application Window
- Email list with unread indicators
- Full email preview with sender details
- Draft editor with refinement controls
- Real-time AI generation with progress feedback

### System Tray Integration
- Background operation
- Quick access menu
- Email refresh notifications

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed Azure AD and API setup
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Complete technical architecture
- **[ROADMAP.md](ROADMAP.md)** - Implementation timeline and tasks

## License

MIT License

## Support

For issues or questions:
- Check the documentation files
- Review logs in `logs/app.log`
- Ensure all credentials are correctly configured in `.env`

---

**Status**: Beta - Desktop UI Functional
**Current Phase**: Phase 3 Complete
**Last Updated**: 2025-11-16
**Version**: 0.3.0
