#!/usr/bin/env python3
"""Personalized Clipboard Concierge - Learns from YOUR behavior.

Tracks what you do after copying things and builds personalized suggestions.
"""
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple
import re

from intent_classifier import IntentClassifier
from action_executor import ActionExecutor


# Configuration
CLIPBOARD_METADATA = Path(__file__).parent.parent.parent / "Data_Storage" / "Clipboard" / "metadata.json"
BEHAVIOR_TRACKER = Path(__file__).parent.parent.parent / "Data_Storage" / "Clipboard_Concierge" / "behavior.json"
PERSONALIZED_SUGGESTIONS = Path(__file__).parent.parent.parent / "Data_Storage" / "Clipboard_Concierge" / "personalized_suggestions.json"
POLL_INTERVAL = 2


class PersonalizedConcierge:
    """Learns from user behavior and provides personalized suggestions."""

    def __init__(self):
        """Initialize the personalized concierge."""
        self.classifier = IntentClassifier()
        self.executor = ActionExecutor()

        self.behavior_file = BEHAVIOR_TRACKER
        self.suggestions_file = PERSONALIZED_SUGGESTIONS

        self.behavior_data = self._load_behavior()
        self.patterns = self._build_patterns()
        self.processed_clipboard_ids = set()

        self._setup_directories()

    def _setup_directories(self):
        """Create necessary directories."""
        self.behavior_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"[PersonalizedConcierge] Behavior tracker initialized")

    def _load_behavior(self) -> Dict:
        """Load tracked user behavior."""
        if not self.behavior_file.exists():
            return {
                "clipboard_events": [],
                "command_history": [],
                "patterns": {}
            }

        try:
            with open(self.behavior_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {
                "clipboard_events": [],
                "command_history": [],
                "patterns": {}
            }

    def _save_behavior(self):
        """Save tracked behavior."""
        with open(self.behavior_file, 'w', encoding='utf-8') as f:
            json.dump(self.behavior_data, f, indent=2, ensure_ascii=False)

    def _build_patterns(self) -> Dict:
        """Build workflow patterns from behavior history."""
        patterns = {
            "workflows": defaultdict(int),  # clipboard -> follow-up actions
            "common_sequences": [],  # sequences of clipboard items
            "context_hints": {},  # what files/paths are related
        }

        # Analyze clipboard history for patterns
        events = self.behavior_data.get("clipboard_events", [])

        # Find sequences: what do you do after copying X?
        for i in range(len(events) - 1):
            current = events[i]
            next_event = events[i + 1]

            # Create a signature from the content
            signature = self._create_signature(current.get("content_preview", ""))

            # Track what typically follows this signature
            follow_up = self._create_signature(next_event.get("content_preview", ""))
            patterns["workflows"][(signature, follow_up)] += 1

        # Extract working directories and common files
        for event in events:
            content = event.get("content_preview", "")

            # Extract working directories
            paths = re.findall(r'[A-Z]:\\[^<>:"|?*\n]+', content)
            for path in paths:
                dir_path = str(Path(path).parent)
                patterns["context_hints"][dir_path] = patterns["context_hints"].get(dir_path, 0) + 1

        return patterns

    def _create_signature(self, content: str) -> str:
        """Create a simplified signature from clipboard content."""
        if not content:
            return "empty"

        content_lower = content.lower()

        # Detect content type
        if re.search(r'\.py\b', content):
            if 'import' in content_lower or 'def ' in content_lower:
                return "python_code"
            return "python_filename"

        if re.search(r'python\s+\w+\.py', content_lower):
            return "python_command"

        if re.search(r'\.json\b', content):
            return "json_file"

        if re.search(r'pip install', content_lower):
            return "pip_install"

        if re.search(r'(error|exception|traceback)', content_lower):
            return "error_message"

        if re.search(r'[A-Z]:\\', content):
            return "file_path"

        if re.search(r'https?://', content):
            return "url"

        # First few words
        words = content.split()[:3]
        return "_".join(words)

    def _get_personalized_suggestion(self, entry: Dict) -> List[str]:
        """Generate personalized suggestions based on patterns."""
        content = entry.get("content_preview", "")
        content_type = entry.get("content_type", "text")

        suggestions = []

        # Get base classification
        classification = self.classifier.classify(content, content_type)
        base_actions = classification.get("suggested_actions", [])

        # Add personalized suggestions based on patterns
        signature = self._create_signature(content)

        # Check what you usually do after copying this type of content
        related_actions = []
        for (clip_sig, follow_sig), count in self.patterns["workflows"].items():
            if clip_sig == signature and count >= 2:  # Happened at least twice
                related_actions.append((follow_sig, count))

        # Sort by frequency
        related_actions.sort(key=lambda x: x[1], reverse=True)

        # Extract context-aware suggestions
        if signature == "python_filename":
            # You usually copy Python filenames and then run them
            if re.search(r'(\w+)\.py', content):
                filename = re.search(r'(\w+)\.py', content)
                if filename:
                    suggestions.append(f"Run: python {filename.group(1)}.py")

        if signature == "pip_install":
            # After pip install, you usually test if it worked
            suggestions.append("Test: python -c 'import <package>'")

        if signature == "error_message":
            # Look for similar errors you've fixed before
            suggestions.append("Check: Did you have this error before?")
            suggestions.append("Search: Your error + 'llama-cpp-python'")

        # Add working directory context
        paths = re.findall(r'[A-Z]:\\[^<>:"|?*\n]+', content)
        if paths:
            working_dir = str(Path(paths[0]).parent)
            if working_dir in self.patterns["context_hints"]:
                suggestions.append(f"Working in: {working_dir}")

        return suggestions

    def track_action(self, clipboard_content: str, action_taken: str):
        """Track what action you took after copying something."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "clipboard_content": clipboard_content[:200],  # Truncate for storage
            "signature": self._create_signature(clipboard_content),
            "action": action_taken
        }

        self.behavior_data["clipboard_events"].append(event)

        # Keep only last 1000 events to avoid growing too large
        if len(self.behavior_data["clipboard_events"]) > 1000:
            self.behavior_data["clipboard_events"] = self.behavior_data["clipboard_events"][-1000:]

        self._save_behavior()

        # Rebuild patterns periodically
        if len(self.behavior_data["clipboard_events"]) % 10 == 0:
            self.patterns = self._build_patterns()

    def process_clipboard_entry(self, entry: Dict):
        """Process a clipboard entry with personalized suggestions."""
        clipboard_id = entry.get('id')
        content_preview = entry.get('content_preview', '')
        content_type = entry.get('content_type', 'text')

        print(f"\n{'='*70}")
        print(f">>> {content_preview[:80]}")
        print(f"{'='*70}")

        # Get base classification
        classification = self.classifier.classify(content_preview, content_type)
        intent = classification.get('intent')

        if intent == 'none':
            print(f">>> No clear intent detected")
            return

        # Get base actions (from if/else rules)
        base_actions = classification.get('suggested_actions', [])

        # Get personalized suggestions (from your behavior)
        personalized = self._get_personalized_suggestion(entry)

        # Combine both
        print(f">>> Agent suggests:")

        # First show personalized suggestions (they're more relevant!)
        if personalized:
            for suggestion in personalized:
                print(f"   [P] {suggestion}")  # [P] for personalized

        # Then show standard actions
        action_labels = {
            'create_calendar_event': 'Add to Calendar',
            'set_reminder': 'Set Reminder',
            'search_stackoverflow': 'Search Stack Overflow',
            'search_google': 'Google Search',
            'open_file': 'Open File',
        }

        for action in base_actions[:3]:  # Show top 3
            label = action_labels.get(action, action)
            print(f"   [*] {label}")  # [*] for standard

        # Track this clipboard event
        self.track_action(content_preview, f"classified_as_{intent}")

    def monitor(self):
        """Monitor clipboard and provide personalized suggestions."""
        print("="*70)
        print("PERSONALIZED CLIPBOARD CONCIERGE")
        print("="*70)
        print(f"[PersonalizedConcierge] Learning from your behavior...")
        print(f"[PersonalizedConcierge] Patterns learned: {len(self.patterns['workflows'])}")
        print(f"[PersonalizedConcierge] Press Ctrl+C to stop\n")

        while not CLIPBOARD_METADATA.exists():
            print(f"[PersonalizedConcierge] Waiting for clipboard metadata...")
            time.sleep(5)

        print(f"[PersonalizedConcierge] Started monitoring\n")

        try:
            while True:
                # Load clipboard metadata
                try:
                    with open(CLIPBOARD_METADATA, 'r', encoding='utf-8') as f:
                        clipboard_entries = json.load(f)
                except (json.JSONDecodeError, IOError):
                    clipboard_entries = []

                # Process new entries
                for entry in clipboard_entries:
                    entry_id = entry.get('id')

                    if entry_id and entry_id not in self.processed_clipboard_ids:
                        self.process_clipboard_entry(entry)
                        self.processed_clipboard_ids.add(entry_id)

                # Sleep before next poll
                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print(f"\n[PersonalizedConcierge] Stopped by user")
            print(f"[PersonalizedConcierge] Patterns learned: {len(self.patterns['workflows'])}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Personalized Clipboard Concierge")
    parser.add_argument(
        '--once',
        action='store_true',
        help='Analyze once and exit'
    )

    args = parser.parse_args()

    concierge = PersonalizedConcierge()

    if args.once:
        concierge.analyze_once()
    else:
        concierge.monitor()


if __name__ == "__main__":
    main()
