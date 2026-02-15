#!/usr/bin/env python3
"""Test the new formatted output with friendly labels."""

from clipboard_concierge import ClipboardConcierge

# Create test entry
test_entry = {
    "id": "test_formatting_001",
    "timestamp": "2026-02-15T00:20:00.000000",
    "content_type": "text",
    "content_preview": "Meeting with the product team tomorrow at 3:30 PM to discuss the new features",
    "file_path": None,
    "source": "clipboard"
}

# Create concierge and process
concierge = ClipboardConcierge(auto_execute=False)

print("\n" + "="*70)
print("CLIPBOARD CONCIERGE - Formatted Output Test")
print("="*70)

concierge.process_clipboard_entry(test_entry)

print("\n" + "="*70)
