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

### Running

```bash
python src/main.py
```

## Usage

### First Launch
1. App will prompt for Microsoft account authentication
2. Approve permissions for email access
3. App will analyze your recent sent emails to learn your style
4. System tray icon will appear when ready

### Drafting Emails
1. Click system tray icon or press `Ctrl+Alt+E`
2. Select an email from your inbox
3. Click "Generate Draft"
4. Review and refine as needed
5. Copy to Outlook or send directly

### Hotkeys (Default)
- `Ctrl+Alt+E`: Show/hide main window
- `Ctrl+Alt+D`: Generate draft for selected email
- `Ctrl+Alt+R`: Refine current draft
- `Ctrl+Alt+C`: Copy draft to clipboard

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

## Development Phases

- [x] Phase 1: Foundation & Authentication
- [ ] Phase 2: AI Integration & Style Learning
- [ ] Phase 3: Desktop UI Development
- [ ] Phase 4: Draft Refinement & Polish
- [ ] Phase 5: Advanced Features
- [ ] Phase 6: Web Dashboard (Optional)

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed implementation timeline.

## Contributing

This is a personal project, but suggestions and improvements are welcome.

## Privacy & Security

- All email data is stored locally in SQLite
- API credentials stored securely using OS keyring
- No data sent to third parties except Microsoft Graph API and Claude API
- Clear cache and data options available in settings

## License

MIT License (or your preferred license)

## Support

For issues or questions, please refer to the project documentation or create an issue.

---

**Status**: In Development
**Current Phase**: Phase 1 - Foundation
**Last Updated**: 2025-11-16
