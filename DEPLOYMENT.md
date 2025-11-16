# Deployment Guide - Email Drafting Tool

Complete step-by-step guide to deploy and configure the Email Drafting Tool.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Azure AD App Registration](#step-1-azure-ad-app-registration)
3. [Step 2: Get Anthropic API Key](#step-2-get-anthropic-api-key)
4. [Step 3: Clone & Install](#step-3-clone--install)
5. [Step 4: Configure Environment](#step-4-configure-environment)
6. [Step 5: First Run (CLI Setup)](#step-5-first-run-cli-setup)
7. [Step 6: Launch Desktop App](#step-6-launch-desktop-app)
8. [Step 7: Verify Everything Works](#step-7-verify-everything-works)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Python**: Version 3.11 or higher
- **Microsoft Account**: Outlook.com or Office 365 account
- **Internet Connection**: Required for API access
- **Disk Space**: ~500 MB (including dependencies)

### Check Python Version
```bash
python --version
# Should show Python 3.11.x or higher
# If not, download from https://www.python.org/downloads/
```

---

## Step 1: Azure AD App Registration

This allows the app to access your Microsoft Outlook emails.

### 1.1 Go to Azure Portal

1. Open browser and go to: **https://portal.azure.com**
2. Sign in with your Microsoft account (same one you use for Outlook)

### 1.2 Navigate to App Registrations

1. In the search bar at the top, type: **"App registrations"**
2. Click on **"App registrations"** in the results
3. Click **"+ New registration"** button (top left)

### 1.3 Register the Application

**Application Details:**
- **Name**: `Email Drafting Tool` (or any name you prefer)
- **Supported account types**: Select **"Accounts in any organizational directory and personal Microsoft accounts"**
  - This allows both work and personal Outlook accounts
- **Redirect URI**:
  - Platform: Select **"Public client/native (mobile & desktop)"**
  - URI: Enter `http://localhost:8000/callback`

Click **"Register"** button at the bottom.

### 1.4 Copy Your Credentials

After registration, you'll see the app overview page.

**Copy these TWO values** (you'll need them in Step 4):

1. **Application (client) ID**
   - Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
   - Copy this entire ID

2. **Directory (tenant) ID**
   - Example: `9z8y7x6w-v5u4-3t2s-1r0q-ponmlkjihgfe`
   - Copy this entire ID
   - If using personal Outlook.com account, you can use `common` instead

**⚠️ Save these values in a text file temporarily - you'll need them soon!**

### 1.5 Configure API Permissions

1. In the left sidebar, click **"API permissions"**
2. Click **"+ Add a permission"** button
3. Click **"Microsoft Graph"**
4. Click **"Delegated permissions"**
5. Search for and check these permissions:
   - ✅ `Mail.Read` - Read user mail
   - ✅ `Mail.ReadWrite` - Read and write access to user mail
   - ✅ `Mail.Send` - Send mail as user (optional)
   - ✅ `User.Read` - Sign in and read user profile

6. Click **"Add permissions"** button at the bottom
7. *(Optional)* Click **"Grant admin consent for [your account]"** if you have admin rights
   - If not, you'll grant consent when you first use the app

### 1.6 Enable Public Client Flow

1. In the left sidebar, click **"Authentication"**
2. Scroll down to **"Advanced settings"**
3. Find **"Allow public client flows"**
4. Toggle **"Enable the following mobile and desktop flows"** to **YES**
5. Click **"Save"** at the top

**✅ Azure AD Setup Complete!** You now have your Client ID and Tenant ID.

---

## Step 2: Get Anthropic API Key

This enables the AI-powered draft generation.

### 2.1 Go to Anthropic Console

1. Open browser and go to: **https://console.anthropic.com**
2. Sign up or log in with your account

### 2.2 Create API Key

1. After logging in, look for **"API Keys"** in the left sidebar
2. Click **"+ Create Key"** button
3. Give it a name: `Email Drafting Tool`
4. Click **"Create Key"**

### 2.3 Copy Your API Key

**IMPORTANT**: The API key will only be shown ONCE!

- It looks like: `sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Copy it immediately** and save it securely
- You won't be able to see it again (but you can create a new one if lost)

**⚠️ Save this key in the same text file with your Azure credentials!**

### 2.4 Add Credits (If Needed)

- Anthropic offers $5 free credits for new accounts
- If you need more, go to **"Settings" → "Billing"** to add payment method
- Typical usage: ~$2-5 per month for 100 drafts

**✅ Anthropic Setup Complete!** You now have your API key.

---

## Step 3: Clone & Install

### 3.1 Navigate to Project Directory

```bash
# Go to where you cloned the repo
cd /path/to/emailv2

# Or if you haven't cloned yet:
# git clone <your-repo-url>
# cd emailv2
```

### 3.2 Create Virtual Environment

This keeps dependencies isolated from your system Python.

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

You should see `(venv)` appear in your terminal prompt.

### 3.3 Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 3.4 Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- PyQt6 (desktop UI)
- anthropic (Claude AI)
- msal (Microsoft authentication)
- sqlalchemy (database)
- beautifulsoup4, html2text (email parsing)
- And all other dependencies

**Wait time**: 2-5 minutes depending on your internet speed.

**Expected output**: You should see packages being downloaded and installed.

**✅ Installation Complete!** All dependencies are now installed.

---

## Step 4: Configure Environment

### 4.1 Create .env File

```bash
# Copy the example file
cp .env.example .env
```

### 4.2 Edit .env File

**On macOS/Linux:**
```bash
nano .env
# Or use your preferred editor: vim, code, etc.
```

**On Windows:**
```bash
notepad .env
# Or use: code .env (if you have VS Code)
```

### 4.3 Fill In Your Credentials

Update these lines with your actual values from Steps 1 and 2:

```env
# Microsoft Graph API (from Step 1)
AZURE_CLIENT_ID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
AZURE_TENANT_ID=common
AZURE_REDIRECT_URI=http://localhost:8000/callback

# Anthropic API (from Step 2)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Leave these as default:
DATABASE_PATH=./data/emailv2.db
CACHE_DIR=./cache
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
AUTO_FETCH_INTERVAL=300
MAX_EMAILS_PER_FETCH=20
INITIAL_STYLE_LEARNING_EMAILS=200
THEME=dark
```

**Important Values to Change:**
1. ✏️ `AZURE_CLIENT_ID` - Replace with YOUR Client ID from Azure
2. ✏️ `AZURE_TENANT_ID` - Use `common` for personal accounts, or your tenant ID
3. ✏️ `ANTHROPIC_API_KEY` - Replace with YOUR API key from Anthropic

**Save the file** (Ctrl+O, Enter, Ctrl+X in nano; Ctrl+S in notepad)

### 4.4 Verify .env File

```bash
# Check that file exists
ls -la .env

# Quick verification (won't show secrets)
cat .env | grep AZURE_CLIENT_ID
# Should show: AZURE_CLIENT_ID=a1b2c3d4-... (your actual ID)
```

**✅ Configuration Complete!** Your credentials are now set.

---

## Step 5: First Run (CLI Setup)

This step authenticates, fetches emails, and learns your writing style.

### 5.1 Run the CLI Application

```bash
python src/main.py
```

### 5.2 What Will Happen

**Step 1/4 - Database Initialization:**
```
[1/4] Initializing database...
  ✓ Database initialized
    - Total emails in DB: 0
    - Inbox: 0, Sent: 0
```

**Step 2/4 - Cache:**
```
[2/4] Initializing cache...
  ✓ Cache initialized
    - Cached entries: 0
```

**Step 3/4 - Authentication:**

You'll see something like:
```
[3/4] Authenticating with Microsoft Graph API...
  ! Authentication required

================================================================================
MICROSOFT AUTHENTICATION REQUIRED
================================================================================
To sign in, use a web browser to open the page:
https://microsoft.com/devicelogin

And enter the code: A1B2C3D4
================================================================================

Waiting for authentication...
```

### 5.3 Complete Microsoft Authentication

1. **Open your web browser**
2. **Go to**: https://microsoft.com/devicelogin
3. **Enter the code** shown in your terminal (e.g., `A1B2C3D4`)
4. **Click "Next"**
5. **Sign in** with your Microsoft account (the one you use for Outlook)
6. **Review permissions** - you'll see what the app can access:
   - Read your email
   - Send email on your behalf
   - Read your profile
7. **Click "Accept"** or "Yes"
8. **You'll see**: "You have signed in to Email Drafting Tool on your device"
9. **Return to your terminal**

The terminal should now show:
```
✓ Authentication successful!
================================================================================

  ✓ Authenticated as: Your Name (your.email@outlook.com)
```

**Step 4/4 - Fetch Emails:**
```
[4/4] Fetching emails from Microsoft Outlook...
  - Fetching inbox emails...
    ✓ Fetched 20 inbox emails (20 new)
  - Fetching sent emails for style learning...
    ✓ Fetched 50 sent emails (50 new)
```

**Step 5/6 - Style Learning:**
```
[5/6] Learning your writing style from sent emails...
  - Analyzing sent emails...
    ✓ Analyzed 47 emails
    - Average email length: 142 words
    - Formality level: Professional
    - Common greetings: Hi, Hello, Good morning
    - Style: Professional and clear communication style with...
  - Building sender-specific profiles...
    ✓ Created 12 sender profiles
```

**Step 6/6 - Sample Draft:**
```
[6/6] Generating sample draft response...
  - Generating draft for: "Q4 Budget Review Meeting"
    From: sarah@company.com
    ✓ Draft generated successfully!
    - Tokens used: 1250
    - Draft version: 1

────────────────────────────────────────────────────────────────
DRAFT PREVIEW:
────────────────────────────────────────────────────────────────
Hi Sarah,

Thanks for reaching out about the Q4 budget review. I've reviewed
the preliminary numbers and have a few thoughts...
────────────────────────────────────────────────────────────────
```

**Final Summary:**
```
================================================================================
PHASE 2 COMPLETE - AI INTEGRATION & STYLE LEARNING
================================================================================

📊 Current Status:
  - Total emails in database: 70
  - Inbox emails: 20
  - Sent emails: 50
  - Unread emails: 5
  - Sender profiles: 12

📝 Your Writing Style:
  - Emails analyzed: 47
  - Average length: 142 words
  - Formality score: 0.65/1.0
  - Tone: professional, clear, concise
  - Summary: Professional and clear communication style...

⚙️  Configuration:
  - Database: ./data/emailv2.db
  - Cache: ./cache
  - Logs: ./logs/app.log
  - AI Model: claude-3-5-sonnet-20241022

✅ Phase 1 Complete:
  [✓] Microsoft Graph authentication
  [✓] Database setup and initialization
  [✓] Email fetching and storage
  [✓] Cache service

✅ Phase 2 Complete:
  [✓] Claude AI integration
  [✓] Writing style analysis
  [✓] Sender profile building
  [✓] Draft generation engine
  [✓] Refinement system
```

**✅ CLI Setup Complete!** You're now ready for the desktop app.

### 5.4 Verify Data

Check that everything was stored:

```bash
# Check database exists
ls -lh data/emailv2.db
# Should show file size (e.g., 245K)

# Check cache
ls -lh cache/
# Should show token cache file

# Check logs
tail -n 20 logs/app.log
# Should show recent log entries
```

---

## Step 6: Launch Desktop App

Now that everything is configured, launch the GUI!

### 6.1 Start the Desktop Application

```bash
python run_gui.py
```

### 6.2 What You'll See

A window will open (1400x900 pixels) with:

**Left Pane (Email List):**
- Filter dropdown: "Unread" selected
- List of unread emails with:
  - Sender name
  - Subject line
  - Date/time
  - Bold ● indicator for unread

**Middle Pane (Email Details):**
- "Select an email to view details"

**Right Pane (Draft Editor):**
- Draft controls (Length, Tone dropdowns)
- "🤖 Generate Draft" button
- Refinement buttons (disabled until draft generated)
- Empty text editor

**Status Bar (Bottom):**
- "Ready - 5 emails"

**System Tray:**
- Look for an icon in your system tray (taskbar on Windows, menu bar on Mac)

### 6.3 Generate Your First Draft

1. **Click on an email** in the left pane
   - Email details appear in the middle pane

2. **Review the email content**
   - Read the sender, subject, and body

3. **Choose draft options** (or leave as default):
   - Length: Medium
   - Tone: Auto

4. **Click "🤖 Generate Draft"** button
   - Progress bar appears
   - Wait 3-5 seconds
   - Draft appears in the editor!

5. **Review the generated draft**
   - Check if it matches your style
   - See the version info at the bottom

6. **Refine if needed** (click any button):
   - ✂️ Make Concise
   - 📝 Add Details
   - 👔 More Formal
   - 😊 More Casual
   - ✓ Fix Grammar
   - • Add Bullets

7. **Use the draft:**
   - Click "📋 Copy to Clipboard"
   - Go to Outlook and paste
   - OR click "📧 Create Draft in Outlook" to create it directly

**✅ Desktop App Working!** You can now draft emails with AI.

---

## Step 7: Verify Everything Works

### 7.1 Test Checklist

Go through this checklist to verify all features:

- [ ] **Email list displays correctly**
  - Unread emails show with ● indicator
  - Email count is accurate
  - Can click emails to select

- [ ] **Email details show properly**
  - Subject, From, Date display
  - Email body is readable
  - No formatting issues

- [ ] **Draft generation works**
  - Click "Generate Draft" button
  - Progress bar appears
  - Draft appears within 5 seconds
  - Draft makes sense and matches your style

- [ ] **Refinement buttons work**
  - Can click "Make Concise" → draft shortens
  - Can click "More Formal" → tone changes
  - Custom instructions work
  - Version number increments

- [ ] **Actions work**
  - Copy to clipboard → can paste in other apps
  - Create in Outlook → draft appears in Outlook

- [ ] **Menu functions**
  - File → Refresh Emails (fetches new emails)
  - Draft → Generate Draft (works)
  - Help → About (shows info)

- [ ] **Keyboard shortcuts**
  - Ctrl+R refreshes emails
  - Ctrl+D generates draft
  - Ctrl+Q quits app

- [ ] **System tray**
  - Icon appears in tray
  - Right-click shows menu
  - Can hide/show window

### 7.2 Check Your Style Profile

Verify your writing style was learned:

```bash
# View style profile
sqlite3 data/emailv2.db "SELECT total_emails_analyzed, avg_email_length, avg_formality_score, style_summary FROM style_profiles;"
```

Should show something like:
```
47|142|0.65|Professional and clear communication style with moderate formality...
```

### 7.3 Check Sender Profiles

```bash
# View sender profiles
sqlite3 data/emailv2.db "SELECT sender_email, relationship_type, avg_formality_score FROM sender_profiles LIMIT 5;"
```

Should show your frequent contacts:
```
john@company.com|colleague|0.70
sarah@company.com|colleague|0.65
boss@company.com|manager|0.85
```

### 7.4 Check Generated Drafts

```bash
# View drafts
sqlite3 data/emailv2.db "SELECT id, draft_version, subject, length(body_content) FROM drafts ORDER BY created_at DESC LIMIT 3;"
```

Should show recent drafts:
```
1|1|Re: Q4 Budget Meeting|245
2|2|Re: Q4 Budget Meeting|180
3|1|Re: Project Update|320
```

**✅ Everything Verified!** Your email drafting tool is fully operational.

---

## Troubleshooting

### Issue: "Module not found" errors

**Cause**: Dependencies not installed or wrong Python environment

**Solution**:
```bash
# Make sure venv is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Authentication failed" or "Invalid client"

**Cause**: Incorrect Azure credentials in .env

**Solution**:
1. Check `.env` file has correct `AZURE_CLIENT_ID`
2. Verify you copied the full Client ID (with dashes)
3. Make sure there are no extra spaces or quotes
4. Try using `AZURE_TENANT_ID=common` if using personal account

### Issue: "API key is invalid" from Anthropic

**Cause**: Incorrect API key in .env

**Solution**:
1. Check `.env` file has correct `ANTHROPIC_API_KEY`
2. Verify key starts with `sk-ant-`
3. Make sure entire key was copied
4. Try creating a new API key in Anthropic console

### Issue: "No emails found"

**Cause**: No emails in your Outlook account, or permissions not granted

**Solution**:
1. Check you have emails in your Outlook inbox
2. Run `python src/main.py` to fetch emails
3. Verify permissions were granted during authentication
4. Try clicking "File → Refresh Emails" in the app

### Issue: "Failed to generate draft"

**Cause**: API key issue, or no sent emails for style learning

**Solution**:
1. Check logs: `tail -f logs/app.log`
2. Verify you have at least 5-10 sent emails in Outlook
3. Run `python src/main.py` again to re-analyze
4. Check internet connection
5. Verify Anthropic API key is valid

### Issue: GUI won't start or crashes

**Cause**: PyQt6 installation issue or missing dependencies

**Solution**:
```bash
# Reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6

# On Linux, may need system packages:
sudo apt-get install python3-pyqt6  # Ubuntu/Debian
sudo dnf install python3-qt6        # Fedora
```

### Issue: "Permission denied" on database

**Cause**: Multiple instances running or file permissions

**Solution**:
```bash
# Close all instances of the app
pkill -f "python.*run_gui.py"
pkill -f "python.*main.py"

# Fix permissions
chmod 644 data/emailv2.db
```

### Issue: Drafts seem off-style

**Cause**: Not enough sent emails analyzed

**Solution**:
1. Send more emails naturally over a few days
2. Run `python src/main.py` again to re-analyze
3. The more emails analyzed (50-200), the better the results

### Issue: Slow performance

**Cause**: Large database or slow internet

**Solution**:
1. Clear old emails from database:
   ```bash
   sqlite3 data/emailv2.db "DELETE FROM emails WHERE created_at < date('now', '-30 days');"
   ```
2. Check internet speed
3. Reduce `MAX_EMAILS_PER_FETCH` in .env to 10

### Still Having Issues?

1. **Check logs**: `cat logs/app.log | tail -n 50`
2. **Enable debug mode**: Set `DEBUG_MODE=true` in .env
3. **Re-run setup**: Delete `data/` and `cache/` folders, run `python src/main.py` again
4. **Check documentation**: Review SETUP_GUIDE.md and PROJECT_PLAN.md

---

## Next Steps

### Daily Usage

1. **Morning**:
   ```bash
   python run_gui.py
   ```
   Or create a desktop shortcut

2. **Check emails**:
   - New emails auto-refresh every 5 minutes
   - Or click "File → Refresh Emails"

3. **Draft responses**:
   - Select email → Generate Draft → Refine → Use

4. **End of day**:
   - Minimize to tray or quit (Ctrl+Q)

### Improving Style Learning

The tool learns over time. To improve:

1. **Re-analyze periodically**:
   ```bash
   python src/main.py
   ```
   This fetches new sent emails and updates your style profile

2. **Send emails naturally**:
   - The more you email, the better it learns
   - Aim for 50-100 sent emails for best results

3. **Provide feedback**:
   - When you use a draft, it tracks usage
   - Edits you make help improve future drafts

### Customization

Edit `.env` to customize:

- `AUTO_FETCH_INTERVAL=600` - Refresh every 10 minutes
- `MAX_EMAILS_PER_FETCH=50` - Fetch more emails at once
- `THEME=light` - Use light theme
- `LOG_LEVEL=DEBUG` - More detailed logs

---

## Deployment Complete! 🎉

You now have a fully functional AI-powered email drafting tool!

**Summary of what you set up:**
- ✅ Azure AD app for Outlook access
- ✅ Anthropic API for AI drafting
- ✅ Python environment with all dependencies
- ✅ Configured .env file
- ✅ Authenticated and fetched emails
- ✅ Learned your writing style
- ✅ Generated sample drafts
- ✅ Launched desktop application
- ✅ Verified all features work

**You can now:**
- Browse your Outlook emails in a desktop app
- Generate AI-powered draft responses
- Refine drafts with one-click buttons
- Copy drafts or create them in Outlook
- Save 2-3 minutes per email response

**Start drafting smarter emails today!**

---

**Need help?** Check the logs (`logs/app.log`) or re-read the troubleshooting section above.
