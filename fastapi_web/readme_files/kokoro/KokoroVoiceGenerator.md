# Kokoro-82M Voice Generation Module

Comprehensive class-based implementation for generating voices using the Kokoro-82M model. This module provides professional text-to-speech capabilities with support for 16 different voice types and automatic audio file management.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported Voices](#supported-voices)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Audio File Management](#audio-file-management)
- [Error Handling](#error-handling)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

**⚠️ Important**: If you encounter import errors, see [TROUBLESHOOTING.md](../kokoro/TROUBLESHOOTING.md) for detailed solutions.

## Features

✅ **16 Professional Voices** - American, British accents with male/female variants  
✅ **Automatic File Management** - Timestamps, metadata, organization  
✅ **Batch Processing** - Generate multiple voices in one call  
✅ **Audio Normalization** - Automatic loudness control  
✅ **Metadata Tracking** - JSON metadata for each generated audio  
✅ **Error Handling** - Graceful error management with logging  
✅ **GPU Support** - CUDA acceleration when available  
✅ **Flexible Output** - Custom output directories and filenames  

## Installation

### Prerequisites

- Python 3.8+
- PyTorch with CUDA support (optional but recommended)
- torchaudio

### Install Dependencies

```bash
# Basic installation (recommended)
pip install torch torchaudio kokoro-onnx scipy numpy

# GPU support (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install kokoro-onnx scipy numpy

# For audio file saving (scipy is more reliable than torchaudio for WAV format)
pip install scipy
```

**Note**: Use `kokoro-onnx` (not `kokoro`) as the package name. The code internally uses `KPipeline` from the Kokoro library.

## Quick Start

```python
from kokoro_voice_generator import KokoroVoiceGenerator

# Initialize generator
generator = KokoroVoiceGenerator()

# Generate a voice
audio_path, metadata = generator.generate_voice(
    text="Hello, welcome to Kokoro voice generation",
    voice_type="af_sarah"
)

print(f"✅ Generated: {audio_path}")
print(f"Duration: {metadata['duration_seconds']:.2f} seconds")
```

**Output:**
```
✅ Generated: media/voiceover/user/2025-11-11-14-30.wav
Duration: 3.45 seconds
```

## Supported Voices

### American Female Voices
| Code | Name | Age | Description |
|------|------|-----|-------------|
| `af_sarah` | Sarah | Young Adult | Friendly, clear voice |
| `af_nicole` | Nicole | Adult | Professional, warm |
| `af_bella` | Bella | Young Adult | Bright, energetic |
| `af_jessica` | Jessica | Adult | Smooth, confident |
| `af_april` | April | Young Adult | Youthful, cheerful |
| `af_diana` | Diana | Adult | Sophisticated, mature |

### American Male Voices
| Code | Name | Age | Description |
|------|------|-----|-------------|
| `am_michael` | Michael | Adult | Deep, professional |
| `am_david` | David | Middle-Aged | Authoritative, calm |
| `am_john` | John | Adult | Friendly, approachable |
| `am_eric` | Eric | Young Adult | Modern, casual |
| `am_aaron` | Aaron | Young Adult | Youthful, energetic |
| `am_andrew` | Andrew | Adult | Balanced, natural |

### British Female Voices
| Code | Name | Age | Description |
|------|------|-----|-------------|
| `bf_emma` | Emma | Young Adult | Posh, eloquent |
| `bf_grace` | Grace | Adult | Refined, professional |

### British Male Voices
| Code | Name | Age | Description |
|------|------|-----|-------------|
| `bm_lewis` | Lewis | Middle-Aged | Sophisticated, mature |
| `bm_oliver` | Oliver | Young Adult | Modern British, friendly |

## API Reference

### Class: `KokoroVoiceGenerator`

#### Initialization

```python
generator = KokoroVoiceGenerator(
    model_name="kokoro-82m",           # Model identifier
    device=None,                        # 'cuda' or 'cpu' (auto-detect)
    output_base_dir="media/voiceover/user",  # Default output directory
    sample_rate=24000,                 # Audio sample rate (Hz)
    logger=None                        # Custom logger instance
)
```

#### Core Methods

##### `generate_voice()`

Generate a single voice from text.

**Signature:**
```python
def generate_voice(
    text: str,
    voice_type: str = "af_sarah",
    output_dir: Optional[str] = None,
    filename: Optional[str] = None,
    speed: float = 1.0,
    normalize: bool = True,
    save_metadata: bool = True,
    **kwargs
) -> Tuple[str, Dict[str, Any]]:
```

**Parameters:**
- `text` (str): Text to convert to speech (required)
- `voice_type` (str): Voice identifier (default: "af_sarah")
- `output_dir` (str): Custom output directory
- `filename` (str): Custom filename without extension (auto-generated if None)
- `speed` (float): Speech speed multiplier (0.5-2.0, default: 1.0)
- `normalize` (bool): Normalize audio loudness (default: True)
- `save_metadata` (bool): Save metadata JSON file (default: True)
- `**kwargs`: Additional model parameters

**Returns:**
- Tuple containing:
  - `audio_file_path` (str): Path to generated WAV file
  - `metadata` (dict): Audio metadata including duration, sample rate, etc.

**Example:**
```python
audio_path, metadata = generator.generate_voice(
    text="Welcome to our voice service",
    voice_type="af_sarah",
    speed=1.0,
    normalize=True
)

print(f"File: {audio_path}")
print(f"Duration: {metadata['duration_seconds']} seconds")
print(f"Sample Rate: {metadata['sample_rate']} Hz")
```

##### `generate_batch_voices()`

Generate multiple voices efficiently.

**Signature:**
```python
def generate_batch_voices(
    texts: List[str],
    voice_types: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    **kwargs
) -> List[Tuple[str, Dict[str, Any]]]:
```

**Parameters:**
- `texts` (List[str]): List of text strings
- `voice_types` (List[str]): Voice types for each text (repeats if length=1)
- `output_dir` (str): Output directory for all files
- `**kwargs`: Additional parameters passed to generate_voice

**Returns:**
- List of (audio_path, metadata) tuples

**Example:**
```python
texts = [
    "Hello everyone",
    "How are you today?",
    "Welcome to the show"
]

results = generator.generate_batch_voices(
    texts=texts,
    voice_types=["af_sarah", "am_michael", "bf_emma"]
)

for audio_path, metadata in results:
    print(f"{metadata['voice_type']}: {audio_path}")
```

##### `validate_voice_type()`

Check if a voice type is supported.

```python
is_valid = generator.validate_voice_type("af_sarah")  # Returns: True
is_valid = generator.validate_voice_type("invalid")    # Returns: False
```

##### `get_supported_voices()`

Get list of all supported voices.

```python
voices = generator.get_supported_voices()
# Returns: ['af_sarah', 'af_nicole', ..., 'bm_oliver']

print(f"Available voices: {len(voices)}")
```

##### `get_voice_metadata()`

Get detailed information about a specific voice.

```python
metadata = generator.get_voice_metadata("af_sarah")
# Returns: {
#     "name": "Sarah",
#     "gender": "Female",
#     "accent": "American",
#     "age": "Young Adult"
# }
```

##### `get_all_voices_metadata()`

Get metadata for all voices at once.

```python
all_metadata = generator.get_all_voices_metadata()

for voice_id, info in all_metadata.items():
    print(f"{voice_id}: {info['name']} ({info['gender']}, {info['accent']})")
```

##### `list_generated_voices()`

List all previously generated voice files.

```python
voices = generator.list_generated_voices(
    output_dir="media/voiceover/user",
    include_metadata=True
)

for voice in voices:
    print(f"{voice['filename']} - {voice['size_kb']:.1f} KB")
    if 'metadata' in voice:
        print(f"  Duration: {voice['metadata']['duration_seconds']:.2f}s")
```

##### `delete_voice_file()`

Delete a generated voice file.

```python
success = generator.delete_voice_file(
    filename="2025-11-11-14-30.wav",
    delete_metadata=True  # Also delete .json metadata
)

if success:
    print("✅ File deleted successfully")
```

## Usage Examples

### Example 1: Basic Voice Generation

```python
from kokoro_voice_generator import KokoroVoiceGenerator

# Initialize
generator = KokoroVoiceGenerator()

# Generate voice
audio_path, metadata = generator.generate_voice(
    text="This is a test of the voice generation system",
    voice_type="af_sarah"
)

# Display results
print(f"Generated file: {audio_path}")
print(f"Duration: {metadata['duration_seconds']:.2f} seconds")
```

### Example 2: Multiple Voices with Different Speakers

```python
texts = [
    ("Hello, I'm Sarah", "af_sarah"),
    ("Hi, I'm Michael", "am_michael"),
    ("Good morning, it's Emma", "bf_emma"),
]

for text, voice in texts:
    audio_path, _ = generator.generate_voice(
        text=text,
        voice_type=voice
    )
    print(f"✅ {voice}: {audio_path}")
```

### Example 3: Speed Variation

```python
speeds = [0.75, 1.0, 1.25, 1.5]

for speed in speeds:
    audio_path, metadata = generator.generate_voice(
        text="This is a speed test",
        voice_type="af_sarah",
        speed=speed,
        filename=f"speed-{speed}"
    )
    print(f"Speed {speed}: {audio_path}")
```

### Example 4: Batch Processing with Progress

```python
texts = [
    "Good morning",
    "How are you?",
    "Welcome to the system",
    "Thank you for listening",
    "Goodbye everyone"
]

print(f"Generating {len(texts)} voices...")
results = generator.generate_batch_voices(
    texts=texts,
    voice_types=["af_sarah"] * len(texts)  # Use same voice
)

print(f"\n✅ Successfully generated {len(results)} files:")
for i, (audio_path, metadata) in enumerate(results, 1):
    print(f"{i}. {metadata['duration_seconds']:.2f}s: {audio_path}")
```

### Example 5: List and Manage Generated Files

```python
# List all generated voices
voices = generator.list_generated_voices(include_metadata=True)

print(f"Found {len(voices)} generated voices:\n")

total_size = 0
for voice in sorted(voices, key=lambda x: x['created_at'], reverse=True):
    print(f"📁 {voice['filename']}")
    print(f"   Size: {voice['size_kb']:.1f} KB")
    print(f"   Created: {voice['created_at']}")
    
    if 'metadata' in voice:
        meta = voice['metadata']
        print(f"   Voice: {meta['voice_metadata']['name']} ({meta['voice_metadata']['accent']})")
        print(f"   Duration: {meta['duration_seconds']:.2f}s")
    
    total_size += voice['size_kb']

print(f"\n📊 Total size: {total_size:.1f} KB")
```

## Configuration

### Output Directory Structure

By default, files are saved in `media/voiceover/user/`:

```
media/
├── voiceover/
│   └── user/
│       ├── 2025-11-11-14-30.wav
│       ├── 2025-11-11-14-30_metadata.json
│       ├── 2025-11-11-14-31.wav
│       └── 2025-11-11-14-31_metadata.json
```

### Custom Configuration

```python
generator = KokoroVoiceGenerator(
    model_name="kokoro-82m",
    device="cuda",  # Use GPU
    output_base_dir="media/custom/voices",
    sample_rate=22050
)
```

### Timestamp Filename Format

Files are automatically named with current date/time:
- Format: `YYYY-MM-DD-HH-MM.wav`
- Example: `2025-11-11-14-30.wav`
- Metadata: `2025-11-11-14-30_metadata.json`

## Audio File Management

### Generated Files

Each voice generation creates:
1. **WAV file** - Audio in 24-bit WAV format at 24kHz
2. **Metadata JSON** - Complete information about the generation

### Metadata Contents

```json
{
  "text": "Generated text content",
  "voice_type": "af_sarah",
  "voice_metadata": {
    "name": "Sarah",
    "gender": "Female",
    "accent": "American",
    "age": "Young Adult"
  },
  "audio_file": "/full/path/to/audio.wav",
  "sample_rate": 24000,
  "duration_seconds": 3.45,
  "speed": 1.0,
  "normalized": true,
  "generated_at": "2025-11-11T14:30:00.000000",
  "file_size_bytes": 165120
}
```

### File Operations

**List all voices:**
```python
voices = generator.list_generated_voices()
```

**Delete a voice:**
```python
generator.delete_voice_file("2025-11-11-14-30.wav")
```

## Error Handling

### Common Errors

#### 1. Invalid Voice Type

```python
try:
    generator.generate_voice(
        text="Hello",
        voice_type="invalid_voice"
    )
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Unsupported voice type: invalid_voice
```

#### 2. Empty Text

```python
try:
    generator.generate_voice(text="")
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Text cannot be empty after stripping whitespace
```

#### 3. Model Not Available

```python
try:
    generator = KokoroVoiceGenerator()
except ImportError as e:
    print(f"Model error: {e}")
    # Output: Model error: Kokoro model is not installed
```

#### 4. GPU Memory Issues

```python
# Fallback to CPU
generator = KokoroVoiceGenerator(device="cpu")
```

## Best Practices

### 1. Error Handling in Production

```python
try:
    audio_path, metadata = generator.generate_voice(
        text=user_input,
        voice_type=voice_choice
    )
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    return {"error": "Invalid input"}
except RuntimeError as e:
    logger.error(f"Generation failed: {e}")
    return {"error": "Voice generation failed"}
```

### 2. Efficient Batch Processing

```python
# Good: Generate in batches
results = generator.generate_batch_voices(
    texts=large_text_list[:100],  # Process 100 at a time
    voice_types=["af_sarah"] * 100
)
```

### 3. Resource Management

```python
# Use context manager approach (recommended)
generator = KokoroVoiceGenerator(device="cuda")
try:
    results = generator.generate_batch_voices(texts)
finally:
    # Cleanup if needed
    pass
```

### 4. Logging and Monitoring

```python
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
generator = KokoroVoiceGenerator()

# Monitor generation
for audio_path, metadata in results:
    logging.info(f"Generated {metadata['voice_type']}: {audio_path}")
```

### 5. File Organization

```python
from pathlib import Path

# Organize by user or date
user_dir = Path("media/voiceover/user") / user_id
user_dir.mkdir(parents=True, exist_ok=True)

generator.generate_voice(
    text="Hello",
    output_dir=str(user_dir)
)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| GPU out of memory | Switch to CPU: `device="cpu"` |
| Slow generation | Use GPU or reduce batch size |
| Metadata not saving | Check directory permissions |
| Audio quality issues | Disable normalization or adjust speed |
| Model not found | Install: `pip install kokoro` |

## License

This module is part of the Auto Video Generator project.

## Support

For issues or questions, contact the development team.

---

**Last Updated:** 2025-11-11  
**Version:** 1.0.0
