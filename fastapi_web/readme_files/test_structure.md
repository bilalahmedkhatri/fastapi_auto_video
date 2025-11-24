# Test Directory Structure

## Overview
This document describes the component-based organization of test files in the FastAPI application.

## Directory Structure

```
test/
├── api/                    # API endpoint tests
│   ├── free_voiceover_api_test.py
│   └── rate_limit_test.py
│
├── media/                  # Media file tests
│   ├── audio_accessibility_test.py
│   └── audio_playback_test.py
│
├── startup/                # Startup task tests
│   └── startup_tasks_test.py
│
└── ui/                     # UI component tests
    ├── audio_player_test.html
    └── voice_samples_test.html
```

## Component Categories

### 1. API Tests (`test/api/`)
Tests for API endpoints and their functionality.

**Files:**
- `free_voiceover_api_test.py` - Tests the free voiceover tool API endpoint
- `rate_limit_test.py` - Tests rate limiting functionality for API endpoints

**Purpose:**
- Verify API endpoint responses
- Test request/response handling
- Validate rate limiting behavior
- Ensure proper error handling

### 2. Media Tests (`test/media/`)
Tests for media file handling, accessibility, and playback.

**Files:**
- `audio_accessibility_test.py` - Tests audio file URL accessibility
- `audio_playback_test.py` - Tests audio generation and playback functionality

**Purpose:**
- Verify generated audio files are accessible via HTTP
- Test audio file serving through static routes
- Validate audio file generation
- Check media file metadata and headers

### 3. Startup Tests (`test/startup/`)
Tests for application initialization and startup tasks.

**Files:**
- `startup_tasks_test.py` - Tests application startup task execution

**Purpose:**
- Validate startup task logic
- Test voice sample initialization
- Verify database seeding
- Check model preloading behavior

### 4. UI Tests (`test/ui/`)
HTML-based tests for user interface components.

**Files:**
- `audio_player_test.html` - Interactive test for audio player functionality
- `voice_samples_test.html` - Interactive test for voice sample player

**Purpose:**
- Manual browser-based testing
- Verify audio playback in browsers
- Test UI component rendering
- Validate user interaction flows

## Naming Conventions

### Test Files
- **Suffix pattern:** `*_test.py` or `*_test.html`
- **Example:** `audio_playback_test.py` (not `test_audio_playback.py`)

### Directory Names
- **Lowercase:** All directory names use lowercase
- **Descriptive:** Names reflect the component being tested
- **No prefixes:** Avoid `test_` prefix in directory names

## Adding New Tests

When adding new test files:

1. **Identify the component** being tested (API, media, startup, UI, etc.)
2. **Choose the appropriate directory** based on component category
3. **Follow naming convention:** `component_name_test.py` or `component_name_test.html`
4. **Create new categories** if testing a new component type not covered above

### Example: Adding a Database Test
```bash
# Create new directory
mkdir test/database

# Add test file
# Name: database_connection_test.py (not test_database_connection.py)
```

## Running Tests

### Python Tests
```bash
# Run all Python tests
python -m pytest test/

# Run specific category
python -m pytest test/api/
python -m pytest test/media/
python -m pytest test/startup/

# Run specific test file
python -m pytest test/api/rate_limit_test.py
```

### HTML Tests
Open HTML files directly in a browser:
```bash
# Windows
start test/ui/audio_player_test.html

# macOS
open test/ui/audio_player_test.html

# Linux
xdg-open test/ui/audio_player_test.html
```

## Best Practices

1. **One component per test file** - Keep tests focused on a single component
2. **Descriptive file names** - Use names that clearly indicate what's being tested
3. **Proper categorization** - Place tests in the correct subdirectory
4. **Documentation** - Add docstrings to test files explaining their purpose
5. **Maintainability** - Keep test structure aligned with source code structure

## Historical Notes

**Reorganization Date:** November 23, 2025

**Previous Structure:**
- All test files were in root directory with `test_*` prefix
- Files were later moved to `test/` directory
- Initial organization used `test/voiceover/` subdirectory

**Current Structure:**
- Component-based subdirectories (`api/`, `media/`, `startup/`, `ui/`)
- Suffix naming convention (`*_test.py`, `*_test.html`)
- Clear separation by functionality

**Migration Summary:**
```
Root directory test files → test/ directory → Component subdirectories
test_*.py                 → *_test.py       → test/component/*_test.py
```

## Future Considerations

As the application grows, consider adding:
- `test/database/` - Database operations tests
- `test/auth/` - Authentication/authorization tests
- `test/integration/` - Integration tests
- `test/performance/` - Performance/load tests
- `test/security/` - Security tests

---

**Last Updated:** November 23, 2025  
**Maintainer:** Development Team
