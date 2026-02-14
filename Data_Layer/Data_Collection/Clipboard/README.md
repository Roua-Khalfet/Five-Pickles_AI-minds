# Clipboard Watcher - MemoryOS Data Ingestion Module

Automatically captures text, URLs, images, and files from system clipboard for local MemoryOS database ingestion.

## Quick Start

```bash
# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the watcher
python clipboard_watcher.py
```

The watcher will run silently in the background. Press `Ctrl+C` to stop it.

## What It Captures

- **Text**: Any text content copied to clipboard
- **URLs**: Automatically detected and categorized separately from plain text
- **Images**: Screenshots and images copied to clipboard (Windows)
- **Files**: File lists when you copy files in Windows Explorer + creates actual file duplicates

## Features

- **Deduplication**: Skips identical content within 5 seconds to avoid duplicates
- **Silent operation**: Runs in background with minimal console output
- **File duplication**: When you copy files, it creates actual copies in `data/copied_files/`
- **Image metadata**: Captures dimensions, format, size, and color mode
- **Standardized schema**: Compatible with other MemoryOS modules for ChromaDB ingestion

## Output Structure

```
clipboard_watcher/
├── clipboard_watcher.py     # Main script
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── data/
    ├── text/
    │   └── metadata.json           # All clipboard events metadata
    ├── images/
    │   ├── clip_20260214_143022_123456.png
    │   └── clip_20260214_143125_789012.png
    ├── files/
    │   └── files_20260214_185525_454343.json  # File list metadata
    └── copied_files/
        ├── document.pdf            # Duplicated files
        └── image.png
```

## Metadata Schema

All clipboard events are logged to `data/text/metadata.json`:

```json
{
  "id": "md5_hash_of_content",
  "timestamp": "2026-02-14T18:54:07.332950",
  "content_type": "text|url|image|files",
  "content_preview": "First 200 chars or description",
  "file_path": "path/to/captured/file (for images/files)",
  "source": "clipboard",
  "image_info": {              // For images only
    "width": 1920,
    "height": 1080,
    "format": "PNG",
    "mode": "RGB",
    "size_bytes": 245672
  },
  "copied_files": [            // For files only
    "data/copied_files/document.pdf"
  ]
}
```

File lists are saved to `data/files/`:

```json
{
  "timestamp": "2026-02-14T18:54:07.332950",
  "file_paths": [
    "C:\\Users\\user\\Downloads\\document.pdf"
  ],
  "count": 1
}
```

## Configuration

Edit constants in `clipboard_watcher.py`:

- `POLL_INTERVAL = 1.0` - Check clipboard every 1 second
- `DEDUP_WINDOW = 5.0` - Skip duplicates within 5 seconds
- `CONTENT_PREVIEW_LENGTH = 200` - Text preview length
- `IMAGES_FOLDER = "data/images"` - Where to save images
- `FILES_FOLDER = "data/files"` - Where to save file metadata
- `COPIED_FILES_FOLDER = "data/copied_files"` - Where to duplicate actual files

## Platform Support

| Platform | Text | URL | Image | Files | Notes |
|----------|------|-----|-------|-------|-------|
| Windows  | ✅   | ✅  | ✅    | ✅    | Fully supported (pywin32) |
| macOS    | ✅   | ✅  | ⚠️    | ❌    | Text/URL only (files not supported) |
| Linux    | ✅   | ✅  | ❌    | ❌    | Text/URL only |

## How It Works

1. **Polling**: Checks clipboard every 1 second for new content
2. **Detection**: Detects clipboard format (text, URL, image, files)
3. **Deduplication**: Computes MD5 hash and checks last 5 seconds to avoid duplicates
4. **Capture**: Saves content to appropriate folder with timestamp
5. **Metadata**: Appends event to `data/text/metadata.json`

## Team Integration

This module outputs metadata in the **standardized MemoryOS schema** for compatibility with:
- `downloads_watcher/`
- `screenshots_watcher/`
- `email_watcher/`
- `calendar_watcher/`

All modules append to their respective `metadata.json` files for downstream ChromaDB ingestion.

## Demo Output

```
[ClipboardWatcher] Started monitoring clipboard...
[ClipboardWatcher] Text → data/text/metadata.json
[ClipboardWatcher] Images → data/images
[ClipboardWatcher] Files → data/files
[ClipboardWatcher] Copied files → data/copied_files
✅ Captured URL: https://github.com/memoryos/project
✅ Captured text: This is regular text, not a URL
✅ Captured image: clip_20260214_143022_123456.png (1920x1080)
✅ Captured files: 1 file(s) -> data/copied_files/document.pdf
```

## Dependencies

- **pyperclip** (>=1.8.2): Cross-platform clipboard text access
- **Pillow** (>=10.0.0): Image processing and clipboard grab
- **pywin32** (>=306): Windows-specific clipboard operations (Windows only)

No external APIs - all local/offline processing.

## Notes

- **Windows Clipboard History (Win+V)**: Does not display files - this is normal Windows behavior
- **File permissions**: Some system files may not be copied due to permission restrictions
- **Memory usage**: Deduplication cache only keeps last 5 seconds of history
- **Background operation**: Designed to run continuously as a background service

## Troubleshooting

**Watcher not capturing files?**
- Ensure you're copying files in Windows Explorer (Ctrl+C on selected files)
- Check that files exist in the source location
- Some system/protected files may not be accessible

**Multiple captures of same content?**
- The deduplication window is 5 seconds - if you wait longer, it will capture again
- This is intentional behavior to allow re-capturing after changes

**Images not capturing?**
- Ensure you're using Windows (primary platform)
- Check that pywin32 and Pillow are installed
