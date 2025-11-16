# Setup Guide - Email Drafting Tool

This guide will walk you through setting up the Email Drafting Tool from scratch.

---

## Prerequisites

### 1. System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Python**: Version 3.11 or higher
- **Internet Connection**: Required for API access
- **Microsoft Account**: Personal or work account with Outlook/Office 365

### 2. Required Accounts
- **Microsoft Account**: For accessing your emails via Graph API
- **Anthropic Account**: For Claude AI API access

---

## Step 1: Azure AD App Registration

This allows the application to access your emails via Microsoft Graph API.

### 1.1 Create App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Sign in with your Microsoft account
3. Search for "Azure Active Directory" or "Microsoft Entra ID"
4. In the left sidebar, click **"App registrations"**
5. Click **"+ New registration"**

### 1.2 Configure Application

**Application Name**: `Email Drafting Tool` (or your preferred name)

**Supported account types**: Select one of:
- **Personal Microsoft accounts only** (if using personal Outlook.com)
- **Accounts in any organizational directory and personal Microsoft accounts** (recommended for flexibility)

**Redirect URI**:
- Platform: **Public client/native (mobile & desktop)**
- URI: `http://localhost:8000/callback`

Click **"Register"**

### 1.3 Note Your Credentials

After registration, you'll see the app overview page:

1. **Application (client) ID**: Copy this (e.g., `12345678-1234-1234-1234-123456789abc`)
2. **Directory (tenant) ID**: Copy this as well

Save these values - you'll need them for the `.env` file.

### 1.4 Configure API Permissions

1. In your app registration, click **"API permissions"** in the left sidebar
2. Click **"+ Add a permission"**
3. Select **"Microsoft Graph"**
4. Select **"Delegated permissions"**
5. Add the following permissions:
   - `Mail.Read` - Read user mail
   - `Mail.ReadWrite` - Read and write access to user mail
   - `Mail.Send` - Send mail as user (optional, for direct sending)
   - `User.Read` - Sign in and read user profile

6. Click **"Add permissions"**
7. Click **"Grant admin consent"** if you have admin rights, or request consent

### 1.5 Configure Authentication

1. Click **"Authentication"** in the left sidebar
2. Under "Advanced settings", find **"Allow public client flows"**
3. Set **"Enable the following mobile and desktop flows"** to **Yes**
4. Click **"Save"**

---

## Step 2: Get Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **"API Keys"**
4. Click **"Create Key"**
5. Give it a name (e.g., "Email Drafting Tool")
6. Copy the API key (starts with `sk-ant-...`)

**Important**: Save this key securely - you won't be able to see it again!

---

## Step 3: Project Setup

### 3.1 Clone and Install

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd emailv2

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env   # or use your preferred editor
```

Update the following values in `.env`:

```env
# From Azure AD App Registration
AZURE_CLIENT_ID=your_client_id_from_step_1.3
AZURE_TENANT_ID=common  # or your specific tenant ID

# From Anthropic Console
ANTHROPIC_API_KEY=sk-ant-your_api_key_from_step_2

# Other settings can remain as defaults
```

### 3.3 Create Required Directories

```bash
mkdir -p data cache logs
```

---

## Step 4: First Run & Authentication

### 4.1 Initial Launch

```bash
python src/main.py
```

### 4.2 Microsoft Authentication Flow

On first launch, you'll see:

```
To sign in, use a web browser to open the page:
https://microsoft.com/devicelogin

And enter the code: XXXXXXXXX
```

1. Open your web browser
2. Go to https://microsoft.com/devicelogin
3. Enter the code displayed in your terminal
4. Sign in with your Microsoft account
5. Accept the permission requests
6. Return to the application

The app will save your authentication token securely using your system's keyring.

### 4.3 Initial Style Learning

The application will:
1. Fetch your recent sent emails (last 200 by default)
2. Analyze your writing style
3. Create your initial style profile
4. Build sender-specific profiles

This may take 2-5 minutes depending on email volume.

---

## Step 5: Basic Usage

### 5.1 Main Window

After setup, the app will show:
- **Email List**: Your recent unread emails
- **Email Preview**: Selected email content
- **Draft Panel**: Generated draft responses

### 5.2 Generate Your First Draft

1. Select an email from the list
2. Click **"Generate Draft"** button
3. Wait 3-5 seconds for AI generation
4. Review the draft in the editor

### 5.3 Refine the Draft

Click one of the refinement buttons:
- **"Make Concise"**: Shorter version
- **"Add Details"**: Expanded version
- **"More Formal"**: Professional tone
- **"More Casual"**: Friendly tone
- **"Fix Grammar"**: Grammar and spelling only
- **"Custom"**: Enter your own instruction

### 5.4 Use the Draft

Once satisfied:
- **"Copy to Clipboard"**: Copy and paste into Outlook
- **"Create Draft in Outlook"**: Automatically create draft in your Outlook
- **"Send"**: Send directly (if enabled)

---

## Step 6: Hotkeys Setup

### 6.1 Default Hotkeys

- `Ctrl+Alt+E`: Show/hide main window
- `Ctrl+Alt+D`: Generate draft for selected email
- `Ctrl+Alt+R`: Refine current draft
- `Ctrl+Alt+C`: Copy draft to clipboard

### 6.2 Customize Hotkeys

1. Click **"Settings"** in the main window
2. Go to **"Hotkeys"** tab
3. Click on a hotkey to change it
4. Press your desired key combination
5. Click **"Save"**

---

## Step 7: Advanced Configuration

### 7.1 Style Learning Settings

**Settings → Style Learning**

- **Enable Continuous Learning**: Analyzes new sent emails automatically
- **Minimum Emails for Profile**: How many emails before creating sender profile (default: 5)
- **Re-analyze Interval**: How often to update your style profile (default: weekly)
- **Exclude Senders**: List email addresses to exclude from style learning

### 7.2 Draft Generation Settings

**Settings → Drafts**

- **Default Draft Length**: Short / Medium / Long
- **Formality Level**: Auto / Casual / Professional / Formal
- **Enable Grammar Check**: Always check grammar before showing draft
- **Use Corporate Best Practices**: Apply professional email guidelines

### 7.3 Email Monitoring

**Settings → Monitoring**

- **Auto-fetch Interval**: How often to check for new emails (default: 5 minutes)
- **Max Emails to Fetch**: Limit per fetch (default: 20)
- **Folders to Monitor**: Select which Outlook folders to monitor

---

## Troubleshooting

### Authentication Issues

**Problem**: "Authentication failed" or "Token expired"

**Solution**:
1. Delete cached tokens: `rm -rf cache/tokens/`
2. Restart the application
3. Re-authenticate through device code flow

### API Rate Limits

**Problem**: "Too many requests" error

**Solution**:
- Increase `AUTO_FETCH_INTERVAL` in `.env` to reduce API calls
- Clear cache: `rm -rf cache/`

### Missing Dependencies

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
pip install --upgrade -r requirements.txt
```

### Database Errors

**Problem**: "Database is locked" or corruption errors

**Solution**:
1. Close all instances of the app
2. Backup database: `cp data/emailv2.db data/emailv2.db.backup`
3. Delete database: `rm data/emailv2.db`
4. Restart app (will create fresh database)

### PyQt6 Installation Issues on Linux

**Problem**: PyQt6 fails to install

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt6

# Fedora
sudo dnf install python3-qt6

# Then retry: pip install -r requirements.txt
```

---

## Privacy & Security Notes

### What Data is Stored Locally?

- Email content (for style learning)
- Sender profiles
- Draft history
- Your writing style profile
- API tokens (in system keyring)

### What Data is Sent to External APIs?

**Microsoft Graph API**:
- Your authentication token
- Email fetch requests

**Anthropic Claude API**:
- Email content you're responding to
- Your style profile (as part of prompts)
- Generated drafts

**Note**: Neither Microsoft nor Anthropic retains your data beyond processing the request.

### How to Clear Your Data

**Clear all local data**:
```bash
rm -rf data/ cache/ logs/
```

**Clear just the cache**:
```bash
rm -rf cache/
```

**Revoke API access**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your app registration
3. Delete the app registration

---

## Getting Help

### Common Issues

1. Check the logs: `tail -f logs/app.log`
2. Enable debug mode in `.env`: `DEBUG_MODE=true`
3. Review error messages in the UI

### Support Channels

- **Documentation**: See `PROJECT_PLAN.md` for technical details
- **GitHub Issues**: Report bugs or request features
- **Email**: (your support email)

---

## Next Steps

Now that you're set up:

1. **Use it regularly**: The more you use it, the better it learns your style
2. **Provide feedback**: Use the refinement features to improve drafts
3. **Customize settings**: Adjust to your preferences
4. **Explore advanced features**: Templates, sender-specific tones, etc.

---

**Setup Complete!** 🎉

You're ready to start drafting emails with AI assistance.

---

**Last Updated**: 2025-11-16
**Version**: 1.0
