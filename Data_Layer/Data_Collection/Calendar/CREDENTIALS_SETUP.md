# Google Calendar Credentials Setup Guide

Follow these steps to set up Google Calendar API access for MemoryOS.

## Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Sign in with your Google account
3. Click "Select a project" > "New Project"
4. Name it: "MemoryOS" or any name you prefer
5. Click "Create"

## Step 2: Enable Google Calendar API

1. In the left sidebar, go to **APIs & Services** > **Library**
2. Search for "Google Calendar API"
3. Click on it and press **Enable**

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** (if you have a personal account)
3. Click **Create**
4. Fill in:
   - App name: `MemoryOS Calendar Watcher`
   - User support email: (your email)
   - Developer contact: (your email)
5. Click **Save and Continue**
6. Skip "Scopes" (click Save and Continue)
7. Skip "Test Users" (click Save and Continue)
8. Click **Back to Dashboard**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **+ Create Credentials** at the top
3. Select **OAuth client ID**
4. Application type: **Desktop app**
5. Name: `MemoryOS Calendar`
6. Click **Create**

## Step 5: Download Credentials

1. After creation, a dialog will appear with your credentials
2. Click the **Download JSON** icon (download arrow)
3. The file will be named something like `client_id_123456.json`
4. Rename it to `credentials.json`
5. Move it to: `calendar_watcher/credentials.json`

**⚠️ IMPORTANT**: Never share this file or commit it to Git!

## Step 6: Verify Setup

Your `calendar_watcher/` folder should now have:

```
calendar_watcher/
├── credentials.json  ✅ (Downloaded from Google Cloud)
├── calendar_watcher.py
├── requirements.txt
├── README.md
└── .gitignore  (excludes credentials.json)
```

## Step 7: Run the Watcher

```bash
cd calendar_watcher

# Install dependencies
pip install -r requirements.txt

# Run (first time will open browser for authentication)
python calendar_watcher.py
```

### First Run - OAuth Flow

1. A browser window will open automatically
2. Sign in to your Google account (if not already)
3. Review permissions: "See, edit, download, and permanently delete your calendars"
4. Click **Allow** (the script only reads, never edits)
5. You'll be redirected to a localhost page with a success message
6. The script will continue in the terminal

A `token.pickle` file will be created - you won't need to authenticate again.

## Troubleshooting

### "credentials.json not found"
- Make sure the file is named exactly `credentials.json` (not `.txt`)
- Check it's in the same directory as `calendar_watcher.py`
- Verify the file isn't empty

### "Invalid client secret"
- Download credentials again from Google Cloud Console
- Make sure you selected "Desktop app" as application type

### Authentication fails / browser doesn't open
- Try running: `python calendar_watcher.py --noauth_local_webserver` (if supported)
- Check your firewall/antivirus settings
- Make sure port isn't blocked

### "API has not been enabled"
- Go back to Google Cloud Console
- Navigate to APIs & Services > Library
- Search for and enable "Google Calendar API"

### Want to use a different Google account?
- Delete `token.pickle`
- Run the script again
- It will prompt for authentication with a new account

## Security Notes

- ✅ The script uses **read-only** scope
- ✅ Credentials are stored locally
- ✅ Credentials are excluded from Git (.gitignore)
- ✅ Token automatically refreshes when needed

## Need Help?

For detailed setup, see: README.md

For Google Calendar API documentation:
https://developers.google.com/calendar/api/v3/reference
