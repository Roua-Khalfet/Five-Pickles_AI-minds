#!/usr/bin/env python3
"""Demo personalized suggestions based on user's clipboard history."""

from personalized_concierge import PersonalizedConcierge
from intent_classifier import IntentClassifier
import json

# Load clipboard history
with open('../../Data_Storage/Clipboard/metadata.json', 'r', encoding='utf-8') as f:
    clipboard_data = json.load(f)

print('='*70)
print('LEARNING FROM YOUR CLIPBOARD HISTORY')
print('='*70)

# Analyze patterns
print(f'\nTotal clipboard events: {len(clipboard_data)}')

# Show what we can learn
python_files = [e for e in clipboard_data if '.py' in e.get('content_preview', '')]
print(f'\nPython files copied: {len(python_files)}')

commands = [e for e in clipboard_data if 'python ' in e.get('content_preview', '').lower()]
print(f'Python commands: {len(commands)}')

errors = [e for e in clipboard_data if 'error' in e.get('content_preview', '').lower() or 'traceback' in e.get('content_preview', '').lower()]
print(f'Error messages: {len(errors)}')

# Show examples of personalized learning
print(f'\n' + '='*70)
print('EXAMPLES OF WHAT YOU\'VE BEEN DOING:')
print('='*70)

# Find specific patterns
print('\n[Pattern 1] Working with llama-3.2 model:')
model_entries = [e for e in clipboard_data if 'llama-3.2' in e.get('content_preview', '')]
for entry in model_entries[:3]:
    content = entry.get('content_preview', '')[:70]
    print(f'  - {content}...')

print('\n[Pattern 2] Creating Python scripts:')
script_entries = [e for e in clipboard_data if 'analyze.py' in e.get('content_preview', '') or 'memory_analyzer.py' in e.get('content_preview', '')]
for entry in script_entries[:3]:
    content = entry.get('content_preview', '')[:70]
    print(f'  - {content}...')

print('\n[Pattern 3] Installing llama-cpp-python:')
pip_entries = [e for e in clipboard_data if 'llama-cpp-python' in e.get('content_preview', '')]
for entry in pip_entries[:3]:
    content = entry.get('content_preview', '')[:70]
    print(f'  - {content}...')

print('\n' + '='*70)
print('PERSONALIZED SUGGESTIONS EXAMPLE')
print('='*70)

# Simulate what happens when you copy a Python file
test_entry = {
    'id': 'test_001',
    'timestamp': '2026-02-15T01:20:00.000000',
    'content_type': 'text',
    'content_preview': 'memory_analyzer.py',
    'file_path': None,
    'source': 'clipboard'
}

concierge = PersonalizedConcierge()

print('\n>>> When you copy: memory_analyzer.py')
print('>>> Agent suggests:')
print('   [P] Run: python memory_analyzer.py <args>')
print('   [P] Based on your history: You often run Python scripts')
print('   [*] Open File')
