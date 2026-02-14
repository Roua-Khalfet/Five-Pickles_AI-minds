#!/usr/bin/env python3
"""Test Clipboard Concierge with realistic examples."""
import json
from pathlib import Path
from intent_classifier import IntentClassifier

# Test examples covering all intent types
test_cases = [
    {
        "name": "Calendar Event",
        "content": "Meeting with the design team tomorrow at 3:30 PM to discuss the new UI mockups",
        "expected_intent": "calendar"
    },
    {
        "name": "Reminder",
        "content": "Don't forget to call mom about dinner plans this weekend",
        "expected_intent": "reminder"
    },
    {
        "name": "Error Message",
        "content": "ERROR: NullPointerException at com.example.Service.processData(Service.java:142)",
        "expected_intent": "error"
    },
    {
        "name": "Search Query",
        "content": "How do I center a div in CSS flexbox?",
        "expected_intent": "search"
    },
    {
        "name": "Email Contact",
        "content": "You can reach me at john.doe@example.com for any questions",
        "expected_intent": "contact"
    },
    {
        "name": "Phone Number",
        "content": "Call me at +1-555-123-4567 when you get a chance",
        "expected_intent": "contact"
    },
    {
        "name": "File Path (Windows)",
        "content": "The file is at C:\\Users\\Documents\\Projects\\report.pdf",
        "expected_intent": "file"
    },
    {
        "name": "URL",
        "content": "Check out this article: https://www.example.com/how-to-build-ai-agents",
        "content_type": "url",
        "expected_intent": "open_url"
    },
    {
        "name": "Todo with Priority",
        "content": "URGENT: Finish the presentation for tomorrow's meeting",
        "expected_intent": "reminder"
    },
    {
        "name": "Stack Overflow Search",
        "content": "Python error: ModuleNotFoundError: No module named 'pandas' even though it's installed",
        "expected_intent": "error"
    },
]


def main():
    """Run test cases through the intent classifier."""
    print("=" * 80)
    print("CLIPBOARD CONCIERGE - Intent Classifier Test")
    print("=" * 80)

    classifier = IntentClassifier()

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-' * 80}")
        print(f"Test {i}: {test_case['name']}")
        print(f"{'-' * 80}")

        content = test_case['content']
        content_type = test_case.get('content_type', 'text')
        expected = test_case['expected_intent']

        print(f"Content: {content[:80]}{'...' if len(content) > 80 else ''}")

        # Classify
        result = classifier.classify(content, content_type)

        # Show results
        intent = result['intent']
        confidence = result['confidence']

        print(f"\n[+] Detected Intent: {intent} (confidence: {confidence:.2f})")
        print(f"  Expected: {expected}")

        # Check if correct
        is_correct = intent == expected
        status = "[+] CORRECT" if is_correct else "[-] WRONG"

        # Show reasoning
        if result.get('reasoning'):
            print(f"  Reasoning: {result['reasoning']}")

        # Show suggested actions
        actions = result.get('suggested_actions', [])
        if actions:
            print(f"  Suggested Actions:")
            for action in actions:
                print(f"    - {action}")

        # Show extracted data
        extracted = result.get('extracted_data', {})
        if extracted:
            print(f"  Extracted Data: {json.dumps(extracted, indent=4)}")

        print(f"\n  Status: {status}")

        results.append({
            'name': test_case['name'],
            'correct': is_correct,
            'intent': intent,
            'confidence': confidence
        })

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")

    total = len(results)
    correct = sum(1 for r in results if r['correct'])
    accuracy = (correct / total * 100) if total > 0 else 0

    print(f"\nTotal Tests: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.1f}%")

    print(f"\nResults by Intent:")
    intent_counts = {}
    for r in results:
        intent = r['intent']
        if intent not in intent_counts:
            intent_counts[intent] = {'total': 0, 'correct': 0}
        intent_counts[intent]['total'] += 1
        if r['correct']:
            intent_counts[intent]['correct'] += 1

    for intent, counts in sorted(intent_counts.items()):
        acc = (counts['correct'] / counts['total'] * 100) if counts['total'] > 0 else 0
        print(f"  {intent}: {counts['correct']}/{counts['total']} ({acc:.0f}%)")

    print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    main()
