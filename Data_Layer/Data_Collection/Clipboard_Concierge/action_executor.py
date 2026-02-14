#!/usr/bin/env python3
"""Action Executor for Clipboard Concierge.

Executes actions based on classified clipboard intent.
All actions are performed locally on the user's machine.
"""
import os
import webbrowser
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
import platform


class ActionExecutor:
    """Executes actions based on classified intent."""

    def __init__(self, base_dir: Path = None):
        """Initialize the action executor.

        Args:
            base_dir: Base directory for saving generated files
        """
        self.base_dir = base_dir or Path(__file__).parent.parent.parent / "Data_Storage"
        self.concierge_dir = self.base_dir / "Clipboard_Concierge"
        self.events_dir = self.concierge_dir / "events"
        self.reminders_dir = self.concierge_dir / "reminders"

        self._setup_directories()

    def _setup_directories(self):
        """Create necessary directories."""
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.reminders_dir.mkdir(parents=True, exist_ok=True)

    def execute_action(self, action: str, data: Dict, content: str) -> bool:
        """Execute a specific action.

        Args:
            action: The action to execute
            data: Extracted data from the content
            content: Original clipboard content

        Returns:
            True if action was successful, False otherwise
        """
        action_map = {
            'create_calendar_event': self.create_calendar_event,
            'set_reminder': self.create_reminder,
            'create_reminder': self.create_reminder,
            'add_to_todo_list': self.add_to_todo_list,
            'search_stackoverflow': self.search_stackoverflow,
            'search_google': self.search_google,
            'search_wikipedia': self.search_wikipedia,
            'search_github': self.search_github,
            'search_image': self.search_image,
            'open_in_browser': self.open_url,
            'open_file': self.open_file,
            'show_in_folder': self.show_in_folder,
            'open_file_location': self.show_in_folder,
            'save_contact': self.save_contact,
            'send_email': self.send_email,
            'call_phone': self.call_phone,
            'extract_text': self.extract_text_from_image,
        }

        action_func = action_map.get(action)
        if not action_func:
            print(f"[ActionExecutor] Unknown action: {action}")
            return False

        try:
            return action_func(data, content)
        except Exception as e:
            print(f"[ActionExecutor] Error executing {action}: {e}")
            return False

    def create_calendar_event(self, data: Dict, content: str) -> bool:
        """Create an ICS calendar event file.

        Args:
            data: Extracted calendar data
            content: Original clipboard content

        Returns:
            True if successful
        """
        # Generate ICS file content
        now = datetime.now()
        event_start = now + timedelta(hours=1)  # Default: 1 hour from now
        event_end = event_start + timedelta(hours=1)  # Default: 1 hour duration

        # Use extracted data if available
        if 'time' in data:
            # Parse time and set for today
            # (Simplified - real implementation would parse properly)
            pass

        # Create ICS content
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//MemoryOS//Clipboard Concierge//EN
BEGIN:VEVENT
UID:{datetime.now().strftime('%Y%m%d%H%M%S')}@memoryos.local
DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{data.get('title', 'Clipboard Event')}
DESCRIPTION:{content}
DTSTART:{event_start.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{event_end.strftime('%Y%m%dT%H%M%SZ')}
END:VEVENT
END:VCALENDAR"""

        # Save ICS file
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        ics_filename = f"event_{timestamp}.ics"
        cs_path = self.events_dir / ics_filename

        with open(ics_path, 'w', encoding='utf-8') as f:
            f.write(ics_content)

        print(f"[ActionExecutor] Created calendar event: {ics_path}")

        # Open with default calendar app
        if platform.system() == "Windows":
            os.startfile(ics_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', str(ics_path)])
        else:  # Linux
            subprocess.run(['xdg-open', str(ics_path)])

        return True

    def create_reminder(self, data: Dict, content: str) -> bool:
        """Create a reminder file.

        Args:
            data: Extracted reminder data
            content: Original clipboard content

        Returns:
            True if successful
        """
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')

        reminder_data = {
            "id": f"reminder_{timestamp}",
            "timestamp": now.isoformat(),
            "task": data.get('task', content),
            "created_from": "clipboard",
            "status": "pending"
        }

        reminder_filename = f"reminder_{timestamp}.json"
        reminder_path = self.reminders_dir / reminder_filename

        with open(reminder_path, 'w', encoding='utf-8') as f:
            json.dump(reminder_data, f, indent=2, ensure_ascii=False)

        print(f"[ActionExecutor] Created reminder: {reminder_path}")
        print(f"  -> Task: {reminder_data['task']}")

        return True

    def add_to_todo_list(self, data: Dict, content: str) -> bool:
        """Add item to todo list.

        Args:
            data: Extracted data
            content: Original clipboard content

        Returns:
            True if successful
        """
        # For now, same as creating a reminder
        return self.create_reminder(data, content)

    def search_stackoverflow(self, data: Dict, content: str) -> bool:
        """Search Stack Overflow for error or question.

        Args:
            data: Extracted search query data
            content: Original clipboard content

        Returns:
            True if successful
        """
        query = data.get('error_query', content)
        url = f"https://stackoverflow.com/search?q={query}"
        webbrowser.open(url)
        print(f"[ActionExecutor] Searching Stack Overflow: {query}")
        return True

    def search_google(self, data: Dict, content: str) -> bool:
        """Search Google.

        Args:
            data: Extracted search query data
            content: Original clipboard content

        Returns:
            True if successful
        """
        query = data.get('query', content)
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        print(f"[ActionExecutor] Searching Google: {query}")
        return True

    def search_wikipedia(self, data: Dict, content: str) -> bool:
        """Search Wikipedia.

        Args:
            data: Extracted search query data
            content: Original clipboard content

        Returns:
            True if successful
        """
        query = data.get('query', content)
        url = f"https://en.wikipedia.org/wiki/Special:Search?search={query}"
        webbrowser.open(url)
        print(f"[ActionExecutor] Searching Wikipedia: {query}")
        return True

    def search_github(self, data: Dict, content: str) -> bool:
        """Search GitHub for code issues.

        Args:
            data: Extracted search query data
            content: Original clipboard content

        Returns:
            True if successful
        """
        query = data.get('error_query', content)
        url = f"https://github.com/search?q={query}&type=issues"
        webbrowser.open(url)
        print(f"[ActionExecutor] Searching GitHub issues: {query}")
        return True

    def search_image(self, data: Dict, content: str) -> bool:
        """Search Google Images.

        Args:
            data: Extracted data
            content: Original clipboard content (should be image description)

        Returns:
            True if successful
        """
        # Note: This would require OCR or image description
        # For now, open Google Images
        url = "https://images.google.com/"
        webbrowser.open(url)
        print(f"[ActionExecutor] Opening Google Images")
        return True

    def open_url(self, data: Dict, content: str) -> bool:
        """Open URL in default browser.

        Args:
            data: Extracted data containing URL
            content: URL to open

        Returns:
            True if successful
        """
        url = data.get('url', content)
        webbrowser.open(url)
        print(f"[ActionExecutor] Opening URL: {url}")
        return True

    def open_file(self, data: Dict, content: str) -> bool:
        """Open file with default application.

        Args:
            data: Extracted data containing file path
            content: File path

        Returns:
            True if successful
        """
        file_path = data.get('path', content)

        if not Path(file_path).exists():
            print(f"[ActionExecutor] File not found: {file_path}")
            return False

        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', file_path])

        print(f"[ActionExecutor] Opening file: {file_path}")
        return True

    def show_in_folder(self, data: Dict, content: str) -> bool:
        """Show file in file explorer.

        Args:
            data: Extracted data containing file path
            content: File path

        Returns:
            True if successful
        """
        file_path = data.get('path', content)

        if not Path(file_path).exists():
            print(f"[ActionExecutor] File not found: {file_path}")
            return False

        if platform.system() == "Windows":
            subprocess.run(['explorer', '/select,', file_path])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', '-R', file_path])
        else:  # Linux
            subprocess.run(['nautilus', file_path])

        print(f"[ActionExecutor] Showing file in folder: {file_path}")
        return True

    def save_contact(self, data: Dict, content: str) -> bool:
        """Save contact information to file.

        Args:
            data: Extracted contact data
            content: Original clipboard content

        Returns:
            True if successful
        """
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')

        contact_data = {
            "id": f"contact_{timestamp}",
            "timestamp": now.isoformat(),
            "email": data.get('email', ''),
            "phone": data.get('phone', ''),
            "raw_content": content,
            "created_from": "clipboard"
        }

        contact_filename = f"contact_{timestamp}.json"
        contact_path = self.concierge_dir / "contacts" / contact_filename
        contact_path.parent.mkdir(parents=True, exist_ok=True)

        with open(contact_path, 'w', encoding='utf-8') as f:
            json.dump(contact_data, f, indent=2, ensure_ascii=False)

        print(f"[ActionExecutor] Saved contact: {contact_path}")
        print(f"  -> Email: {contact_data['email']}")
        print(f"  -> Phone: {contact_data['phone']}")

        return True

    def send_email(self, data: Dict, content: str) -> bool:
        """Open email client to send email.

        Args:
            data: Extracted contact data
            content: Original clipboard content

        Returns:
            True if successful
        """
        email = data.get('email', '')
        mailto_link = f"mailto:{email}"
        webbrowser.open(mailto_link)
        print(f"[ActionExecutor] Opening email client for: {email}")
        return True

    def call_phone(self, data: Dict, content: str) -> bool:
        """Initiate phone call.

        Args:
            data: Extracted contact data
            content: Original clipboard content

        Returns:
            True if successful
        """
        phone = data.get('phone', '')
        print(f"[ActionExecutor] Phone number detected: {phone}")
        print(f"  -> Please dial manually on your phone")
        return True

    def extract_text_from_image(self, data: Dict, content: str) -> bool:
        """Extract text from image using OCR.

        Args:
            data: Extracted data
            content: Original clipboard content

        Returns:
            True if successful
        """
        print(f"[ActionExecutor] OCR not yet implemented")
        print(f"  -> Would extract text from clipboard image")
        return False
