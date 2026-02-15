# Personalized Clipboard Concierge

## What Makes It Different?

**Standard Clipboard Concierge (if/else rules):**
```
Copy: "SyntaxError: unterminated string"
→ Suggest: [Search Stack Overflow] [Google Search]  // Generic
```

**Personalized Clipboard Concierge (learns from YOU):**
```
Copy: "SyntaxError: unterminated string"
→ Suggest: [P] Check analyze.py line 41  // Knows your file!
         [P] Similar error 2 hours ago - you fixed it by closing triple quote
         [*] Search Stack Overflow
```

## How It Works

1. **Tracks your behavior**: Every time you copy something, it remembers what you do next
2. **Builds patterns**: "When you copy Python files, you usually run them"
3. **Personalizes suggestions**: Based on YOUR actual workflows
4. **Gets smarter**: The more you use it, the better it knows you

## Your Learned Patterns

From analyzing your clipboard history:
- **Python files**: You copied 24 Python files
- **Commands**: You ran 29 Python commands
- **Errors**: You encountered 8 error messages
- **Project**: Working with llama-3.2-1b-instruct model
- **Scripts**: Creating analyze.py, memory_analyzer.py
- **Workflow**: Install llama-cpp-python → Test → Debug → Run

## Usage

### Monitor with Personalized Suggestions
```bash
cd Data_Layer/Data_Collection/Clipboard_Concierge
py -m personalized_concierge
```

### See What It Learned
```bash
py demo_personalized.py
```

## Example Output

```
>>> analyze.py
============================================================
>>> Agent suggests:
   [P] Run: python analyze.py
   [P] You've edited this file 5 times today
   [*] Open File
   [*] Show in Folder
```

## Data Files

- `behavior.json` - Tracks your clipboard events and actions
- `personalized_suggestions.json` - Learned patterns
- `metadata.json` - All suggestions made

## Privacy

- All data stored locally
- No cloud or external APIs
- 100% private - learns from YOUR behavior only

## Future Enhancements

- [ ] Detect recurring errors and solutions
- [ ] Learn command sequences (e.g., "after pip install, always test import")
- [ ] Predict next action based on time of day
- [ ] Suggest based on project context
- [ ] Learn from successful vs failed attempts
