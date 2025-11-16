# Quick Start Guide

Get up and running with the Email Drafting Tool in 5 minutes.

---

## Prerequisites

1. **Python 3.11+** installed
2. **Microsoft Outlook** account (personal or work)
3. **Anthropic API key** (from https://console.anthropic.com)

---

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd emailv2

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

---

## Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required settings:**

```env
# Azure AD (see SETUP_GUIDE.md for detailed instructions)
AZURE_CLIENT_ID=your_client_id_from_azure_portal

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your_api_key_here
```

---

## Step 3: First Run - CLI Mode

Run the command-line version first to:
1. Authenticate with Microsoft
2. Fetch your emails
3. Learn your writing style

```bash
python src/main.py
```

**What happens:**
1. Opens browser for Microsoft authentication
2. You sign in and approve permissions
3. App fetches emails and analyzes your style
4. Generates a sample draft
5. Shows complete status report

**Expected output:**
```
[1/4] Initializing database... ✓
[2/4] Initializing cache... ✓
[3/4] Authenticating with Microsoft Graph API... ✓
[4/4] Fetching emails from Microsoft Outlook... ✓
[5/6] Learning your writing style... ✓
[6/6] Generating sample draft... ✓

PHASE 2 COMPLETE - AI INTEGRATION & STYLE LEARNING
```

---

## Step 4: Launch Desktop UI

After successful CLI setup, launch the GUI:

```bash
python run_gui.py
```

**The application window will open with:**
- 📧 Email list (left pane)
- 📨 Email details (middle pane)
- ✍️ Draft editor (right pane)

---

## Step 5: Generate Your First Draft

### In the GUI:

1. **Select an email** from the list (left pane)
2. **Click "🤖 Generate Draft"** button
3. **Wait 3-5 seconds** for AI generation
4. **Review the draft** in the editor
5. **Refine if needed:**
   - Click "✂️ Make Concise" to shorten
   - Click "📝 Add Details" to expand
   - Click "👔 More Formal" to increase formality
   - Or enter custom instructions

6. **Use the draft:**
   - Click "📋 Copy to Clipboard" → paste into Outlook
   - Click "📧 Create Draft in Outlook" → creates draft directly

---

## Quick Tips

### Keyboard Shortcuts
- `Ctrl+R` - Refresh emails
- `Ctrl+D` - Generate draft
- `Ctrl+C` - Copy draft
- `Ctrl+Q` - Quit application

### Email Filters
Use the dropdown to filter:
- **Unread** - Only unread emails (default)
- **All Inbox** - All inbox emails
- **Sent** - Your sent emails

### Draft Options
Before generating, you can adjust:
- **Length**: Short (50-100 words), Medium (100-200), Long (200-300)
- **Tone**: Auto (adapts to sender), Casual, Professional, Formal

### Refinement Buttons
- **✂️ Make Concise** - Reduces length by ~30%
- **📝 Add Details** - Expands with more context
- **👔 More Formal** - Professional business tone
- **😊 More Casual** - Friendly, relaxed tone
- **✓ Fix Grammar** - Only fixes errors, keeps content same
- **• Add Bullets** - Reorganizes main points as bullets

### System Tray
Minimize the app to system tray for quick access:
- Right-click tray icon for menu
- "Refresh Emails" to fetch new messages
- "Show Window" to bring back main window

---

## Troubleshooting

### "Authentication Required" Error
**Solution**: Run `python src/main.py` first to authenticate via CLI.

### "No emails found"
**Solution**:
1. Click "File → Refresh Emails" in the menu
2. Or run `python src/main.py` to fetch more emails

### "Failed to generate draft"
**Possible causes:**
- Check your `ANTHROPIC_API_KEY` in `.env`
- Ensure you have internet connection
- Check logs: `tail -f logs/app.log`

### Draft seems off-style
**Solution**:
- Run `python src/main.py` again to re-analyze your writing style
- Ensure you have at least 10-20 sent emails in your account
- The more emails analyzed, the better the style learning

### GUI won't start
**Check:**
1. PyQt6 installed: `pip install PyQt6`
2. Virtual environment activated
3. Check logs: `logs/app.log`

---

## What's Next?

### Improve Style Learning
The app learns from your emails. To improve accuracy:
```bash
# Re-run to analyze more sent emails
python src/main.py
```

### View Your Style Profile
```bash
sqlite3 data/emailv2.db "SELECT * FROM style_profiles;"
```

### Check Sender Profiles
```bash
sqlite3 data/emailv2.db "SELECT sender_email, relationship_type, avg_formality_score FROM sender_profiles;"
```

### Advanced Features
- Set auto-refresh interval in `.env`: `AUTO_FETCH_INTERVAL=300`
- Adjust draft token limit: `ANTHROPIC_MODEL=claude-3-5-sonnet-20241022`
- Enable debug mode: `DEBUG_MODE=true`

---

## Daily Workflow

1. **Morning**: Launch app → Click "Refresh Emails"
2. **Select email** → Click "Generate Draft"
3. **Review and refine** if needed
4. **Copy to Outlook** or create draft directly
5. **Minimize to tray** for quick access throughout day

---

## Support

- **Documentation**: See `PROJECT_PLAN.md` for complete technical details
- **Setup Help**: See `SETUP_GUIDE.md` for Azure AD configuration
- **Logs**: Check `logs/app.log` for debugging

---

**You're all set! Start drafting smarter emails.** 🚀
