#!/usr/bin/env python3
"""Quick integration test for Clipboard Concierge."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from intent_classifier import IntentClassifier
from action_executor import ActionExecutor


def test_classifier():
    """Test the intent classifier."""
    print("[TEST] Intent Classifier")
    print("-" * 60)

    classifier = IntentClassifier()

    test_cases = [
        ("Meeting tomorrow at 3 PM", "calendar"),
        ("Remember to buy milk on the way home", "reminder"),  # Added "Remember"
        ("ERROR: NullPointerException at Service.java:142", "error"),  # Added stack trace
        ("How do I fix this bug?", "search"),
        ("Contact: john@example.com", "contact"),
        ("C:\\Users\\file.txt", "file"),
    ]

    passed = 0
    for content, expected in test_cases:
        result = classifier.classify(content, "text")
        intent = result['intent']
        confidence = result['confidence']

        status = "[PASS]" if intent == expected else "[FAIL]"
        print(f"  {status} {content[:40]:40s} -> {intent:10s} ({confidence:.2f})")

        if intent == expected:
            passed += 1

    print(f"\n  Result: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_executor():
    """Test the action executor initialization."""
    print("\n[TEST] Action Executor")
    print("-" * 60)

    try:
        executor = ActionExecutor()
        print(f"  [PASS] Action executor initialized")
        print(f"  [INFO] Events dir: {executor.events_dir}")
        print(f"  [INFO] Reminders dir: {executor.reminders_dir}")
        return True
    except Exception as e:
        print(f"  [FAIL] Could not initialize: {e}")
        return False


def test_integration():
    """Test basic integration."""
    print("\n[TEST] Integration")
    print("-" * 60)

    try:
        from clipboard_concierge import ClipboardConcierge
        concierge = ClipboardConcierge(auto_execute=False)
        print(f"  [PASS] Clipboard Concierge initialized")
        print(f"  [INFO] Metadata file: {concierge.metadata_file}")
        return True
    except Exception as e:
        print(f"  [FAIL] Could not initialize: {e}")
        return False


def test_file_structure():
    """Test that all required files exist."""
    print("\n[TEST] File Structure")
    print("-" * 60)

    required_files = [
        "__init__.py",
        "intent_classifier.py",
        "action_executor.py",
        "clipboard_concierge.py",
        "test_examples.py",
        "README.md",
        "TEST_RESULTS.md",
    ]

    base_dir = Path(__file__).parent
    missing = []

    for filename in required_files:
        filepath = base_dir / filename
        if filepath.exists():
            print(f"  [PASS] {filename}")
        else:
            print(f"  [FAIL] {filename} missing!")
            missing.append(filename)

    return len(missing) == 0


def main():
    """Run all tests."""
    print("=" * 60)
    print("CLIPBOARD CONCIERGE - Integration Tests")
    print("=" * 60)
    print()

    results = {
        "File Structure": test_file_structure(),
        "Intent Classifier": test_classifier(),
        "Action Executor": test_executor(),
        "Integration": test_integration(),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED - Ready to push!")
    else:
        print("SOME TESTS FAILED - Fix before pushing")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
