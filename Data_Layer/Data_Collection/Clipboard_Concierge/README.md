# Clipboard Concierge - MemoryOS Cross-App Action Agent

An intelligent clipboard assistant that analyzes your clipboard content and suggests relevant actions. Built for MemoryOS as part of the AI hackathon project.

## Features

- **100% Local**: No API calls, all processing happens on your machine
- **Rule-Based Intent Classification**: Detects 6 types of clipboard content
- **Action Suggestions**: Suggests relevant actions based on content
- **Auto-Execute Option**: Can automatically execute best action (opt-in)
- **Real-Time Monitoring**: Continuously monitors clipboard for new entries

## Supported Intent Types

### 1. Calendar Events
**Detected patterns:**
- Meeting keywords: "meeting", "call", "zoom", "appointment", etc.
- Time expressions: "3:00 PM", "14:30", "9 AM"
- Date expressions: "tomorrow", "Monday", "Feb 14", etc.

**Actions:**
- Create ICS calendar event file
- Set reminder

**Example:**
```
"Meeting with team tomorrow at 3 PM"
→ Intent: calendar (confidence: 0.7)
→ Actions: create_calendar_event, set_reminder
```

### 2. Reminders / Todos
**Detected patterns:**
- Todo keywords: "todo", "task", "remember", "don't forget"
- Action verbs: "buy", "call", "email", "send", "finish"

**Actions:**
- Create reminder file
- Add to todo list

**Example:**
```
"Remember to buy milk on the way home"
→ Intent: reminder (confidence: 0.5)
→ Actions: create_reminder, add_to_todo_list
```

### 3. Error Messages
**Detected patterns:**
- Error keywords: "error", "exception", "failed", "bug"
- Stack traces: "at file(", "traceback", "line 42"
- Programming languages

**Actions:**
- Search Stack Overflow
- Search Google
- Search GitHub issues

**Example:**
```
"ERROR: NullPointerException at com.example.Main.main:42"
→ Intent: error (confidence: 0.5)
→ Actions: search_stackoverflow, search_github, search_google
```

### 4. Search Queries
**Detected patterns:**
- Question words: "how", "what", "when", "where", "why"
- Definitions: "define", "meaning of"
- Question marks

**Actions:**
- Search Google
- Search Wikipedia

**Example:**
```
"How do I center a div in CSS?"
→ Intent: search (confidence: 0.7)
→ Actions: search_google, search_wikipedia
```

### 5. Contact Information
**Detected patterns:**
- Email addresses
- Phone numbers

**Actions:**
- Save contact
- Send email
- Call phone

**Example:**
```
"Contact: john@example.com or +1-555-123-4567"
→ Intent: contact (confidence: 0.6)
→ Actions: save_contact, send_email, call_phone
```

### 6. File Paths
**Detected patterns:**
- Windows paths: `C:\Users\...\file.txt`
- Unix paths: `/home/user/docs/report.pdf`
- URLs: `https://example.com`

**Actions:**
- Open file
- Show in folder
- Open in browser (for URLs)

**Example:**
```
"C:\Users\Documents\report.pdf"
→ Intent: file (confidence: 0.7)
→ Actions: open_file, show_in_folder
```

## Installation

No additional dependencies required beyond the base MemoryOS setup.

## Usage

### One-Time Analysis
Analyze all existing clipboard entries once:

```bash
cd Data_Layer/Data_Collection/Clipboard_Concierge
python clipboard_concierge.py --once
```

### Continuous Monitoring
Monitor clipboard in real-time:

```bash
python clipboard_concierge.py
```

Press Ctrl+C to stop monitoring.

### Auto-Execute Mode
Automatically execute the best action without confirmation:

```bash
python clipboard_concierge.py --auto-execute
```

## Architecture

```
Clipboard_Concierge/
├── intent_classifier.py    # Rule-based intent detection
├── action_executor.py      # OS-level action execution
├── clipboard_concierge.py  # Main monitoring loop
├── __init__.py
└── README.md
```

### Data Flow

```
Clipboard Watcher
    ↓
Clipboard Metadata (Data_Storage/Clipboard/metadata.json)
    ↓
Clipboard Concierge (monitors metadata)
    ↓
Intent Classifier (analyzes content)
    ↓
Action Executor (performs actions)
    ↓
Concierge Metadata (Data_Storage/Clipboard_Concierge/metadata.json)
```

## Output

### Metadata Schema

Each suggestion is saved to `Data_Storage/Clipboard_Concierge/metadata.json`:

```json
{
  "id": "concierge_20260214231410221698",
  "timestamp": "2026-02-14T23:14:10.221698",
  "clipboard_id": "0ece4d2dd510968a63cdb8d394b917d4",
  "clipboard_timestamp": "2026-02-14T20:52:19.120483",
  "intent": "calendar",
  "confidence": 0.7,
  "reasoning": "Calendar event indicators: meeting keyword, time detected",
  "suggested_actions": ["create_calendar_event", "set_reminder"],
  "extracted_data": {
    "title": "Meeting with team",
    "time": "3:00 PM"
  },
  "content_preview": "Meeting with team tomorrow at 3 PM",
  "action_taken": "suggested"
}
```

## Generated Files

Based on actions taken, files are created in `Data_Storage/Clipboard_Concierge/`:

- `events/` - ICS calendar event files
- `reminders/` - JSON reminder files
- `contacts/` - JSON contact files

## Configuration

Edit constants in `clipboard_concierge.py`:

```python
POLL_INTERVAL = 2  # Check every 2 seconds
AUTO_EXECUTE = False  # Wait for confirmation by default
```

## Technical Details

- **Pattern Matching**: Uses regex patterns for intent detection
- **Confidence Scoring**: Each pattern adds to confidence score (0.0 to 1.0)
- **Threshold**: Actions only suggested if confidence >= 0.3
- **Cross-Platform**: Supports Windows, macOS, and Linux for file operations

## Future Enhancements

- [ ] Natural language processing for better classification
- [ ] Machine learning model for intent prediction
- [ ] OCR for text extraction from images
- [ ] Integration with Calendar API for direct event creation
- [ ] Notification system for action suggestions
- [ ] Custom action definitions by users

## Team

Built by the MemoryOS team for the AI hackathon.

## License

Part of the MemoryOS project.
