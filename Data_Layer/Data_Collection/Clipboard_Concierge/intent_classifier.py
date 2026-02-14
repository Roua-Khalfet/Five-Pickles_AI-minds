#!/usr/bin/env python3
"""Intent Classifier for Clipboard Concierge.

Analyzes clipboard content and classifies it into actionable categories.
Uses rule-based pattern matching - 100% local, no API calls.
"""
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class IntentClassifier:
    """Classifies clipboard content into actionable intents."""

    def __init__(self):
        """Initialize the intent classifier with patterns."""
        # Calendar/Event patterns
        self.calendar_patterns = {
            'meeting': r'\b(meet|meeting|call|zoom|teams| skype|interview|appointment)\b',
            'time': r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)|\d{1,2}\s*(?:AM|PM|am|pm))\b',
            'date_relative': r'\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            'date_absolute': r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2})\b',
            'duration': r'\b(\d+\s*(?:min|hour|hr|minutes|hours))\b',
        }

        # Reminder/Todo patterns
        self.reminder_patterns = {
            'todo_keywords': r'\b(todo|task|reminder|remember|don\'t forget|make sure|need to)\b',
            'priority': r'\b(urgent|important|asap|priority|critical)\b',
        }

        # Error/Debug patterns
        self.error_patterns = {
            'error_keywords': r'\b(error|exception|failed|failure|bug|issue|problem|crash)\b',
            'stack_trace': r'\b(at\s+[\w.]+\(|traceback|file\s+"|line\s+\d+)\b',
            'languages': r'\b(python|javascript|java|cpp|c\+\+|typescript|go|rust|sql)\b',
        }

        # Web search patterns
        self.search_patterns = {
            'question': r'\b(?:how|what|when|where|who|why|which|can you|is there|are there)\b',
            'definition': r'\b(?:define|meaning of|what is|what are)\b',
        }

        # Contact patterns
        self.contact_patterns = {
            'email': r'\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b',
            'phone': r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        }

        # File path patterns
        self.file_patterns = {
            'windows_path': r'[A-Z]:\\(?:[^\\/:*?"<>|]+\\)*[^\\/:*?"<>|]*',
            'unix_path': r'/(?:[^/\0]+/)*[^/\0]*',
            'url': r'https?://[^\s<>"]+|www\.[^\s<>"]+',
        }

    def classify(self, content: str, content_type: str = "text") -> Dict:
        """Classify clipboard content and return intent with confidence.

        Args:
            content: The clipboard content to analyze
            content_type: Type of content (text, url, image, file)

        Returns:
            Dictionary with intent, confidence, and suggested actions
        """
        if not content or len(content.strip()) == 0:
            return self._no_action_response()

        # If content_type is already specific, use that
        if content_type == "url":
            return self._url_response(content)
        elif content_type == "file":
            return self._file_response(content)
        elif content_type == "image":
            return self._image_response()

        # For text content, run through all classifiers
        scores = {}

        # Check each intent category
        scores['calendar'] = self._check_calendar_intent(content)
        scores['reminder'] = self._check_reminder_intent(content)
        scores['error'] = self._check_error_intent(content)
        scores['search'] = self._check_search_intent(content)
        scores['contact'] = self._check_contact_intent(content)
        scores['file'] = self._check_file_intent(content)

        # Find highest scoring intent
        if not scores:
            return self._no_action_response()

        best_intent = max(scores.items(), key=lambda x: x[1]['confidence'])

        # If confidence is too low, return no action
        if best_intent[1]['confidence'] < 0.3:
            return self._no_action_response()

        return {
            'intent': best_intent[0],
            'confidence': best_intent[1]['confidence'],
            'reasoning': best_intent[1]['reasoning'],
            'suggested_actions': best_intent[1]['actions'],
            'extracted_data': best_intent[1].get('data', {}),
            'content_preview': content[:100] + "..." if len(content) > 100 else content
        }

    def _check_calendar_intent(self, content: str) -> Dict:
        """Check if content is a calendar event."""
        score = 0
        matches = []

        content_lower = content.lower()

        # Check for meeting keyword
        if re.search(self.calendar_patterns['meeting'], content_lower, re.IGNORECASE):
            score += 0.4
            matches.append("meeting keyword detected")

        # Check for time
        if re.search(self.calendar_patterns['time'], content, re.IGNORECASE):
            score += 0.3
            matches.append("time detected")

        # Check for date
        if re.search(self.calendar_patterns['date_relative'], content_lower, re.IGNORECASE):
            score += 0.3
            matches.append("relative date detected")
        elif re.search(self.calendar_patterns['date_absolute'], content_lower, re.IGNORECASE):
            score += 0.3
            matches.append("absolute date detected")

        # Check for duration
        if re.search(self.calendar_patterns['duration'], content_lower, re.IGNORECASE):
            matches.append("duration detected")

        if score < 0.4:
            return {'confidence': 0, 'reasoning': '', 'actions': []}

        return {
            'confidence': min(score, 1.0),
            'reasoning': f"Calendar event indicators: {', '.join(matches)}",
            'actions': [
                'create_calendar_event',
                'set_reminder'
            ],
            'data': self._extract_calendar_data(content)
        }

    def _check_reminder_intent(self, content: str) -> Dict:
        """Check if content is a reminder/todo item."""
        content_lower = content.lower()
        score = 0
        matches = []

        # Check for todo keywords
        if re.search(self.reminder_patterns['todo_keywords'], content_lower, re.IGNORECASE):
            score += 0.5
            matches.append("todo keyword detected")

        # Check for priority
        if re.search(self.reminder_patterns['priority'], content_lower, re.IGNORECASE):
            score += 0.2
            matches.append("priority keyword detected")

        # If short text starting with verb, likely a todo
        if len(content.split()) < 10:
            first_word = content.split()[0].lower()
            if first_word in ['buy', 'call', 'email', 'send', 'finish', 'complete', 'start']:
                score += 0.3
                matches.append("action verb detected")

        if score < 0.5:
            return {'confidence': 0, 'reasoning': '', 'actions': []}

        return {
            'confidence': min(score, 1.0),
            'reasoning': f"Reminder indicators: {', '.join(matches)}",
            'actions': [
                'create_reminder',
                'add_to_todo_list'
            ],
            'data': {
                'task': content.strip()
            }
        }

    def _check_error_intent(self, content: str) -> Dict:
        """Check if content is an error message."""
        score = 0
        matches = []

        content_lower = content.lower()

        # Check for error keywords
        if re.search(self.error_patterns['error_keywords'], content_lower, re.IGNORECASE):
            score += 0.3
            matches.append("error keyword detected")

        # Check for stack trace
        if re.search(self.error_patterns['stack_trace'], content, re.IGNORECASE):
            score += 0.5
            matches.append("stack trace pattern detected")

        # Check for programming language references
        if re.search(self.error_patterns['languages'], content_lower, re.IGNORECASE):
            score += 0.2
            matches.append("programming language detected")

        if score < 0.5:
            return {'confidence': 0, 'reasoning': '', 'actions': []}

        # Extract error message for search
        error_match = re.search(r'error[:\s]+([^\n]+)', content_lower, re.IGNORECASE)
        error_query = error_match.group(1) if error_match else content[:100]

        return {
            'confidence': min(score, 1.0),
            'reasoning': f"Error indicators: {', '.join(matches)}",
            'actions': [
                'search_stackoverflow',
                'search_google',
                'search_github'
            ],
            'data': {
                'error_query': error_query.strip()
            }
        }

    def _check_search_intent(self, content: str) -> Dict:
        """Check if content is a search query."""
        content_lower = content.lower()
        score = 0
        matches = []

        # Check for question words
        if re.search(self.search_patterns['question'], content_lower, re.IGNORECASE):
            score += 0.4
            matches.append("question word detected")

        # Check for definition patterns
        if re.search(self.search_patterns['definition'], content_lower, re.IGNORECASE):
            score += 0.5
            matches.append("definition pattern detected")

        # Check if it ends with question mark
        if content.strip().endswith('?'):
            score += 0.3
            matches.append("question mark detected")

        if score < 0.4:
            return {'confidence': 0, 'reasoning': '', 'actions': []}

        return {
            'confidence': min(score, 1.0),
            'reasoning': f"Search indicators: {', '.join(matches)}",
            'actions': [
                'search_google',
                'search_wikipedia'
            ],
            'data': {
                'query': content.strip()
            }
        }

    def _check_contact_intent(self, content: str) -> Dict:
        """Check if content is contact information."""
        score = 0
        matches = []
        data = {}

        # Check for email
        email_match = re.search(self.contact_patterns['email'], content, re.IGNORECASE)
        if email_match:
            score += 0.6
            matches.append("email detected")
            data['email'] = email_match.group(0)

        # Check for phone
        phone_match = re.search(self.contact_patterns['phone'], content, re.IGNORECASE)
        if phone_match:
            score += 0.6
            matches.append("phone number detected")
            data['phone'] = phone_match.group(0)

        if score < 0.6:
            return {'confidence': 0, 'reasoning': '', 'actions': []}

        actions = ['save_contact']
        if data.get('email'):
            actions.append('send_email')
        if data.get('phone'):
            actions.append('call_phone')

        return {
            'confidence': min(score, 1.0),
            'reasoning': f"Contact indicators: {', '.join(matches)}",
            'actions': actions,
            'data': data
        }

    def _check_file_intent(self, content: str) -> Dict:
        """Check if content is a file path."""
        score = 0
        matches = []
        data = {}

        # Check for Windows path
        win_match = re.search(self.file_patterns['windows_path'], content)
        if win_match:
            score += 0.7
            matches.append("Windows path detected")
            data['path'] = win_match.group(0)

        # Check for Unix path
        unix_match = re.search(self.file_patterns['unix_path'], content)
        if unix_match:
            score += 0.7
            matches.append("Unix path detected")
            data['path'] = unix_match.group(0)

        # URLs are handled separately in content_type

        if score < 0.7:
            return {'confidence': 0, 'reasoning': '', 'actions': []}

        return {
            'confidence': min(score, 1.0),
            'reasoning': f"File path indicators: {', '.join(matches)}",
            'actions': [
                'open_file',
                'open_file_location'
            ],
            'data': data
        }

    def _extract_calendar_data(self, content: str) -> Dict:
        """Extract structured calendar data from content."""
        data = {'raw_content': content}

        # Extract time
        time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))', content, re.IGNORECASE)
        if time_match:
            data['time'] = time_match.group(1)

        # Extract date
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', content)
        if date_match:
            data['date'] = date_match.group(1)

        # Extract duration
        duration_match = re.search(r'(\d+\s*(?:min|hour|hr))', content, re.IGNORECASE)
        if duration_match:
            data['duration'] = duration_match.group(1)

        # Extract title (first few words)
        words = content.split()[:8]
        data['title'] = ' '.join(words)

        return data

    def _url_response(self, url: str) -> Dict:
        """Response for URL content type."""
        return {
            'intent': 'open_url',
            'confidence': 1.0,
            'reasoning': 'URL detected in clipboard',
            'suggested_actions': ['open_in_browser'],
            'extracted_data': {'url': url},
            'content_preview': url
        }

    def _file_response(self, file_path: str) -> Dict:
        """Response for file content type."""
        return {
            'intent': 'file',
            'confidence': 1.0,
            'reasoning': 'File path detected in clipboard',
            'suggested_actions': ['open_file', 'show_in_folder'],
            'extracted_data': {'path': file_path},
            'content_preview': file_path
        }

    def _image_response(self) -> Dict:
        """Response for image content type."""
        return {
            'intent': 'image',
            'confidence': 0.7,
            'reasoning': 'Image detected in clipboard - may contain text or error',
            'suggested_actions': [
                'extract_text',
                'search_image'
            ],
            'extracted_data': {},
            'content_preview': '[Image]'
        }

    def _no_action_response(self) -> Dict:
        """Response when no action is suggested."""
        return {
            'intent': 'none',
            'confidence': 0.0,
            'reasoning': 'No clear intent detected',
            'suggested_actions': [],
            'extracted_data': {},
            'content_preview': ''
        }
