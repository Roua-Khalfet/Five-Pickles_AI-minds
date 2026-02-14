# Google Calendar Watcher - MemoryOS Data Ingestion Module

Monitors Google Calendar for events and stores them in standardized MemoryOS schema.

## Quick Start

### 1. Set up Google Cloud Project (First Time Only)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Calendar API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

### 2. Create OAuth 2.0 Credentials (First Time Only)

1. Go to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **+ Create Credentials** > **OAuth client ID**
3. Configure consent screen (if prompted):
   - Choose "External" user type
   - Add app name: "MemoryOS Calendar Watcher"
   - Save and continue
4. Select application type: **Desktop app**
5. Name it "MemoryOS Calendar"
6. Click **Create**
7. Download credentials and rename to `credentials.json`
8. Save to: `calendar_watcher/credentials.json`

**⚠️ IMPORTANT**: Add your email as a test user in OAuth consent screen to avoid "403: access_denied" errors!

### 3. Install and Run

```bash
# Navigate to root directory
cd c:\Users\bousn\data_ingestion

# Activate shared virtual environment
venv\Scripts\activate

# Run calendar watcher
cd calendar_watcher
python calendar_watcher.py
```

**First run:** A browser window will open for Google authentication. Sign in and grant permission.

## What It Captures

- **Event title and description**
- **Start/end time**
- **Location**
- **Attendees** (names, emails, RSVP status)
- **Creator and organizer**
- **Meeting links** (Google Meet, etc.)
- **Event status** (confirmed, tentative, cancelled)

## Features

- **Automatic polling:** Checks calendar every 5 minutes
- **Deduplication:** Only captures new or updated events
- **Incremental capture:** Looks ahead 30 days for events
- **Silent operation:** Runs in background
- **Standardized schema:** Compatible with other MemoryOS modules

## Output Structure

```
calendar_watcher/
├── calendar_watcher.py     # Main script
├── credentials.json        # OAuth credentials (NOT in git)
├── token.pickle           # Auth token (auto-generated)
└── data/
    ├── events/             # Individual event JSON files
    │   ├── event_20260214_143022_12345678.json
    │   └── event_20260214_150125_87654321.json
    └── metadata.json       # All calendar events (MemoryOS schema)
```

## Metadata Schema

All events are logged to `data/metadata.json`:

```json
{
  "id": "unique_hash",
  "timestamp": "2026-02-14T18:54:07.332950",
  "content_type": "calendar_event",
  "content_preview": "Team Standup - 2026-02-15T10:00:00",
  "file_path": "data/events/event_20260214_143022_12345678.json",
  "source": "google_calendar",
  "event_details": {
    "title": "Team Standup",
    "start": "2026-02-15T10:00:00+01:00",
    "end": "2026-02-15T10:30:00+01:00",
    "location": "Google Meet",
    "attendee_count": 5,
    "has_description": true
  }
}
```

## Configuration

Edit constants in `calendar_watcher.py`:

```python
POLL_INTERVAL = 300  # Poll every 5 minutes
LOOKAHEAD_DAYS = 30  # Look ahead 30 days
```

## Security & Privacy

- ✅ **Read-only access** - never modifies your calendar
- ✅ **Local storage** - all data stays on your machine
- ✅ **Credentials protected** - excluded from Git (.gitignore)
- ✅ **OAuth 2.0** - secure authentication

## Troubleshooting

**"403: access_denied" error**
- Add your email as a test user in Google Cloud Console
- Go to "APIs & Services" > "OAuth consent screen" > "Test users"

**No events captured**
- Ensure events are in the future (after today)
- Check events are within next 30 days
- Verify you're using the correct Google account

**Authentication fails**
- Make sure Google Calendar API is enabled in Google Cloud Console
- Check that `credentials.json` is in the `calendar_watcher/` directory
- Delete `token.pickle` and re-authenticate

## Demo Output

```
[CalendarWatcher] Events -> C:\...\calendar_watcher\data\events
[CalendarWatcher] Metadata -> C:\...\calendar_watcher\data\metadata.json
[CalendarWatcher] Authenticated with Google Calendar
[CalendarWatcher] Started monitoring calendar
[CalendarWatcher] Poll interval: 300s

[CalendarWatcher] Polling for events...
  -> Captured: Team Standup (2026-02-15T10:00:00+01:00)
  -> Captured: Product Review (2026-02-15T14:00:00+01:00)
  -> Total new events: 2
```

## Dependencies

- **google-api-python-client** (>=2.100.0): Google Calendar API client
- **google-auth-oauthlib** (>=1.0.0): OAuth authentication
- **google-auth-httplib2** (>=0.2.0): HTTP transport

## Team Integration

This module outputs metadata in the **standardized MemoryOS schema** for compatibility with:
- `clipboard_watcher/`
- `downloads_watcher/`
- `screenshots_watcher/`
- `email_watcher/`

All modules append to their respective `metadata.json` files for downstream ChromaDB ingestion.
