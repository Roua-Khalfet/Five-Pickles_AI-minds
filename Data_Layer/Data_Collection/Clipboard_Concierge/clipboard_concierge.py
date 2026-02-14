#!/usr/bin/env python3
"""Clipboard Concierge - MemoryOS Cross-App Action Agent.

Monitors clipboard activity and suggests intelligent actions based on content.
100% local, no API calls required.
"""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from intent_classifier import IntentClassifier
from action_executor import ActionExecutor


# Configuration
DATA_STORAGE = Path(__file__).parent.parent.parent / "Data_Storage"
CLIPBOARD_METADATA = DATA_STORAGE / "Clipboard" / "metadata.json"
CONCIERGE_METADATA = DATA_STORAGE / "Clipboard_Concierge" / "metadata.json"
POLL_INTERVAL = 2  # Check every 2 seconds
AUTO_EXECUTE = False  # Wait for user confirmation by default


class ClipboardConcierge:
    """Intelligent clipboard assistant that suggests actions."""

    def __init__(self, auto_execute: bool = False):
        """Initialize the Clipboard Concierge.

        Args:
            auto_execute: If True, automatically execute best action.
                         If False, wait for user confirmation.
        """
        self.classifier = IntentClassifier()
        self.executor = ActionExecutor()
        self.auto_execute = auto_execute

        self.metadata_file = CONCIERGE_METADATA
        self.processed_ids = self._load_processed_ids()

        self._setup_directories()

    def _setup_directories(self):
        """Create necessary directories."""
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"[ClipboardConcierge] Metadata -> {self.metadata_file.absolute()}")

    def _load_processed_ids(self) -> set:
        """Load set of already processed clipboard IDs."""
        if not self.metadata_file.exists():
            return set()

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                return {entry.get('clipboard_id') for entry in metadata if entry.get('clipboard_id')}
        except (json.JSONDecodeError, IOError):
            return set()

    def _save_suggestion(self, clipboard_entry: Dict, classification: Dict) -> None:
        """Save suggestion to metadata file.

        Args:
            clipboard_entry: Original clipboard entry
            classification: Classification result with suggestions
        """
        suggestion = {
            "id": f"concierge_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "timestamp": datetime.now().isoformat(),
            "clipboard_id": clipboard_entry.get('id'),
            "clipboard_timestamp": clipboard_entry.get('timestamp'),
            "intent": classification.get('intent'),
            "confidence": classification.get('confidence'),
            "reasoning": classification.get('reasoning'),
            "suggested_actions": classification.get('suggested_actions', []),
            "extracted_data": classification.get('extracted_data', {}),
            "content_preview": classification.get('content_preview'),
            "action_taken": "auto_executed" if self.auto_execute else "suggested"
        }

        # Load existing metadata
        metadata = []
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                try:
                    metadata = json.load(f)
                except json.JSONDecodeError:
                    metadata = []

        metadata.append(suggestion)

        # Save updated metadata
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _get_clipboard_content(self, clipboard_id: str) -> Optional[str]:
        """Retrieve actual clipboard content if needed.

        For text, this would read from the Clipboard metadata.
        For files/images, we'd need to access the actual stored files.

        Args:
            clipboard_id: ID of clipboard entry

        Returns:
            Content string or None
        """
        # For now, we'll work with what's in metadata
        # A full implementation would read the actual content
        return None

    def process_clipboard_entry(self, entry: Dict) -> None:
        """Process a single clipboard entry.

        Args:
            entry: Clipboard metadata entry
        """
        clipboard_id = entry.get('id')
        content_type = entry.get('content_type', 'text')
        content_preview = entry.get('content_preview', '')

        print(f"\n[ClipboardConcierge] Processing clipboard entry...")
        print(f"  -> Type: {content_type}")
        print(f"  -> Content: {content_preview[:60]}...")

        # Classify the intent
        classification = self.classifier.classify(content_preview, content_type)

        intent = classification.get('intent')
        confidence = classification.get('confidence')

        print(f"  -> Intent: {intent} (confidence: {confidence:.2f})")

        if intent == 'none':
            print(f"  -> No action suggested")
            return

        # Show reasoning
        reasoning = classification.get('reasoning', '')
        if reasoning:
            print(f"  -> Reasoning: {reasoning}")

        # Show suggested actions
        actions = classification.get('suggested_actions', [])
        if actions:
            print(f"  -> Suggested actions:")
            for i, action in enumerate(actions, 1):
                print(f"     {i}. {action}")

            # Auto-execute if enabled
            if self.auto_execute and actions:
                best_action = actions[0]
                extracted_data = classification.get('extracted_data', {})

                print(f"\n[ClipboardConcierge] Auto-executing: {best_action}")
                self.executor.execute_action(best_action, extracted_data, content_preview)

        # Save the suggestion
        self._save_suggestion(entry, classification)

    def monitor(self) -> None:
        """Monitor clipboard metadata for new entries."""
        print("=" * 60)
        print("CLIPBOARD CONCIERGE - MemoryOS")
        print("=" * 60)
        print(f"[ClipboardConcierge] Monitoring: {CLIPBOARD_METADATA}")
        print(f"[ClipboardConcierge] Poll interval: {POLL_INTERVAL}s")
        print(f"[ClipboardConcierge] Auto-execute: {self.auto_execute}")
        print("[ClipboardConcierge] Press Ctrl+C to stop\n")

        # Wait for clipboard metadata to exist
        while not CLIPBOARD_METADATA.exists():
            print(f"[ClipboardConcierge] Waiting for clipboard metadata...")
            time.sleep(5)

        print(f"[ClipboardConcierge] Started monitoring clipboard\n")

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

                    if entry_id and entry_id not in self.processed_ids:
                        self.process_clipboard_entry(entry)
                        self.processed_ids.add(entry_id)

                # Sleep before next poll
                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print(f"\n[ClipboardConcierge] Stopped by user")
            print(f"[ClipboardConcierge] Total suggestions made: {len(self.processed_ids)}")

    def analyze_once(self) -> None:
        """Analyze all unprocessed clipboard entries once and exit."""
        print("=" * 60)
        print("CLIPBOARD CONCIERGE - One-time Analysis")
        print("=" * 60)

        if not CLIPBOARD_METADATA.exists():
            print(f"[ClipboardConcierge] No clipboard metadata found")
            return

        # Load clipboard metadata
        try:
            with open(CLIPBOARD_METADATA, 'r', encoding='utf-8') as f:
                clipboard_entries = json.load(f)
        except (json.JSONDecodeError, IOError):
            clipboard_entries = []

        print(f"\n[ClipboardConcierge] Found {len(clipboard_entries)} clipboard entries")

        # Process all unprocessed entries
        new_count = 0
        for entry in clipboard_entries:
            entry_id = entry.get('id')

            if entry_id and entry_id not in self.processed_ids:
                self.process_clipboard_entry(entry)
                self.processed_ids.add(entry_id)
                new_count += 1

        if new_count == 0:
            print(f"\n[ClipboardConcierge] No new entries to process")
        else:
            print(f"\n[ClipboardConcierge] Processed {new_count} new entries")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Clipboard Concierge - MemoryOS")
    parser.add_argument(
        '--auto-execute',
        action='store_true',
        help='Automatically execute suggested actions without confirmation'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Analyze once and exit instead of continuous monitoring'
    )

    args = parser.parse_args()

    concierge = ClipboardConcierge(auto_execute=args.auto_execute)

    if args.once:
        concierge.analyze_once()
    else:
        concierge.monitor()


if __name__ == "__main__":
    main()
