# CloudLens: AI Vision Camera for CircuitPython

**Professional AI-powered camera system for microcontrollers.** CloudLens integrates hardware cameras with Anthropic's Claude Vision API for real-time image analysis. Capture photos and receive instant AI-powered insights through 12 specialized prompt modes.

**Based on** [OpenAI Image Descriptors with Memento](https://learn.adafruit.com/openai-image-descriptors-with-memento?view=all) by Liz Clark for Adafruit Industries. Extensively modified for Claude Vision API with production-grade optimizations and features.

---

## Quick Start

**For experienced users:**

1. Flash CircuitPython 10.x to PyCamera S3
2. Install libraries: `adafruit_pycamera`, `adafruit_requests`, `adafruit_display_text`, `jpegio`
3. Copy `code.py` and `settings.toml` to CIRCUITPY drive
4. Edit `settings.toml`: Add WiFi credentials and Anthropic API key (`sk-ant-...`)
5. Insert FAT32-formatted SD card
6. Reset device

**Controls:** SHUTTER (capture), LEFT/RIGHT (prompts), UP/DOWN (quality), SELECT (browse), OK (close)

---

## Key Features

- **Real-Time AI Vision**: Capture and analyze with Claude Sonnet 4.5
- **12 Creative Prompts**: Descriptions, art analysis, haiku, translation, identification, storytelling
- **4 Quality Modes**: LOW/MEDIUM/HIGH/ULTRA with automatic size management
- **Smart Auto-Flash**: 5-point brightness detection for low-light scenes
- **Browse Mode**: Review and re-analyze saved images
- **Scrollable Display**: Multi-page text viewer for long responses
- **Professional UI**: Branded viewfinder with quality indicators
- **Zero Hardcoded Values**: 100% configuration via `settings.toml`
- **Production-Ready**: Bulletproof error handling, memory optimization, retry logic

---

## Technical Specifications

### Performance
- **Image Capture**: <1s from shutter to API call
- **API Response**: 2-10s depending on complexity
- **Memory Optimization**: Strategic `gc.collect()` and immediate cleanup
- **Brightness Detection**: 5-point sampling with integer math

### Image Handling
- **Max Image Size**: 3072 KB (3 MB) - configurable
- **Max API Payload**: 5 MB raw, 7 MB base64-encoded
- **Supported Resolutions**: 240×240 to 2560×1920 (13 levels)
- **Format**: JPEG with dynamic quality adjustment
- **Storage**: SD card (FAT32), unlimited capacity

### Network & API
- **WiFi**: 2.4GHz only (ESP32-S3 limitation)
- **API Model**: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- **Max Tokens**: 1024 (configurable)
- **Timeout**: 120 seconds (configurable)
- **Retry Logic**: 3 attempts with exponential backoff
- **Rate Limiting**: Automatic retry with delay

### Memory & Stability
- **CircuitPython Version**: 10.x required
- **Garbage Collection**: 18 strategic collection points
- **Error Handling**: 100% specific exceptions (zero bare `except` blocks)
- **Memory Cleanup**: Immediate `del` after large operations

---

## Hardware Requirements

### Required
- **Microcontroller**: Adafruit PyCamera S3 (ESP32-S3 based)
- **Camera Module**: OV5640 or compatible (built-in on PyCamera)
- **Display**: 240×240 pixel TFT (built-in on PyCamera)
- **SD Card**: Any size, FAT32 formatted
- **WiFi**: 2.4GHz network access
- **Power**: USB-C or battery (500mA recommended)

### Recommended
- **SD Card**: Class 10 or better for faster writes
- **WiFi**: Strong signal for reliable API calls
- **Anthropic API**: Active API key with credits

---

## Installation

### 1. Flash CircuitPython 10.x
Download and install CircuitPython 10.x for PyCamera S3 from [circuitpython.org](https://circuitpython.org/board/adafruit_pycamera_s3/)

### 2. Install Libraries
Copy these libraries from the CircuitPython bundle to `CIRCUITPY/lib/`:
- `adafruit_pycamera/` (folder)
- `adafruit_requests.mpy`
- `adafruit_display_text/` (folder)
- `jpegio.mpy`

### 3. Install CloudLens
Copy to CIRCUITPY drive:
- `code.py` → `CIRCUITPY/code.py`
- `settings.toml` → `CIRCUITPY/settings.toml`

### 4. Configure Settings
Edit `settings.toml` with your credentials:
```toml
CIRCUITPY_WIFI_SSID = "your-network-name"
CIRCUITPY_WIFI_PASSWORD = "your-wifi-password"
ANTHROPIC_API_KEY = "sk-ant-your-api-key-here"
```

### 5. Insert SD Card
Format SD card as FAT32, insert into PyCamera S3

### 6. Reset Device
Press reset button or reconnect USB. Look for "CloudLens" on display.

---

## Configuration

All settings are in `settings.toml`. The file is fully documented with comments.

### Essential Settings

**Network & API:**
```toml
CIRCUITPY_WIFI_SSID = "YourNetwork"
CIRCUITPY_WIFI_PASSWORD = "password123"
ANTHROPIC_API_KEY = "sk-ant-api03-..."
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
CLAUDE_MAX_TOKENS = 1024
```

**Camera & Quality:**
```toml
CAMERA_RESOLUTION = 3              # 0-12 (3 = 800×600)
DEFAULT_QUALITY_MODE = "MEDIUM"    # LOW, MEDIUM, HIGH, ULTRA
AUTO_FLASH_ENABLED = true
DARK_THRESHOLD = 30                # 0-255, lower = more sensitive
```

**Display:**
```toml
TEXT_SCALE = 2                     # Font size multiplier
TEXT_WRAP_WIDTH = 20               # Characters per line
LINES_PER_PAGE = 7                 # Lines visible per screen
```

**Network Tuning:**
```toml
WIFI_TIMEOUT = 30                  # Seconds
WIFI_RETRY_ATTEMPTS = 3
API_TIMEOUT = 120                  # Seconds
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 2                # Seconds between retries
```

### Resolution Codes
```
0: 240×240     4: 1024×768    8: 1920×1080    12: 2560×1920
1: 320×240     5: 1280×720    9: 2048×1536
2: 640×480     6: 1280×1024   10: 2560×1440
3: 800×600     7: 1600×1200   11: 2560×1600
```

---

## Usage

### Controls

| Button | Action | Function |
|--------|--------|----------|
| **SHUTTER** (short) | Capture | Take photo and analyze with current prompt |
| **SHUTTER** (long) | Autofocus | Focus camera before capture |
| **LEFT/RIGHT** | Navigate | Cycle through prompt modes |
| **UP/DOWN** | Quality/Scroll | Change quality mode or scroll text |
| **SELECT** | Browse | Enter/exit saved image browser |
| **OK** | Confirm/Close | Send browsed image or close text viewer |

### Viewfinder Display

```
┌─────────────────────────────────────┐
│ CloudLens                           │ ← Branding
│                                     │
│         [LIVE VIEWFINDER]           │
│                                     │
│                                     │
│  DESCRIBE                ** MEDIUM  │ ← Prompt & Quality
└─────────────────────────────────────┘
```

**Display Elements:**
- **Top-left**: CloudLens branding (green)
- **Bottom-left**: Current prompt mode (cyan, large)
- **Bottom-right**: Quality mode with icon (cyan)

### Quality Modes

| Mode | Resolution | Target Size | Max Expected | Use Case |
|------|------------|-------------|--------------|----------|
| **LOW** | 640×480 | 300 KB | 400 KB | Quick captures, data conservation |
| **MEDIUM** | 800×600 | 600 KB | 800 KB | Balanced quality/speed (default) |
| **HIGH** | 1024×768 | 1000 KB | 1300 KB | Detailed analysis |
| **ULTRA** | 1280×720 | 1400 KB | 1800 KB | Maximum detail, fine print |

**Note:** Images exceeding 3 MB will be rejected with error message.

### Prompt Modes

1. **DESCRIBE** - Accessibility-focused alt text descriptions
2. **ART_ANALYSIS** - Formal art critique (composition, color, technique)
3. **HAIKU** - Three-line poetry inspired by the image
4. **TRANSLATE** - OCR text extraction and translation to English
5. **ALIEN** - Whimsical alien perspective on Earth objects
6. **WEIRD** - Anomaly detection and unusual element identification
7. **MOVIE** - Dramatic movie title and tagline generation
8. **PLANT** - Plant species identification and care info
9. **CAR** - Automotive design analysis
10. **DRAMA** - Soap opera-style storytelling
11. **STUDY** - Educational tutoring for study materials
12. **KINDNESS** - Moments of human connection and compassion

### Workflow

1. **Power On** → Wait for "READY!" message (green)
2. **Select Prompt** → LEFT/RIGHT to choose mode
3. **Adjust Quality** → UP/DOWN for resolution
4. **Compose Shot** → Frame your subject
5. **Capture** → Press SHUTTER
6. **Wait** → "SNAP!" → "Sending to Claude..."
7. **Read Response** → UP/DOWN to scroll, OK to close
8. **Browse** → SELECT to review saved images

---

## Customization

### Adding Custom Prompts

1. **Define your prompt** in `settings.toml`:
```toml
MYMODE_LABEL = "My Custom Mode"
MYMODE_PROMPT = "Describe this image as if you were a detective investigating a crime scene."
```

2. **Add to prompt order**:
```toml
PROMPT_ORDER = "DESCRIBE,MYMODE,HAIKU,..."
```

3. **Reset device** to load new prompt

### Custom Quality Modes

Define custom quality presets:
```toml
quality_CUSTOM_resolution = "5"        # 1280×720
quality_CUSTOM_label = "CUSTOM 720p"
quality_CUSTOM_target_kb = "800"
quality_CUSTOM_max_expected_kb = "1000"
quality_CUSTOM_icon = "++"
```

Then add "CUSTOM" to `QUALITY_MODE_ORDER` in code.py

---

## Troubleshooting

### WiFi Issues

**Connection Failed**
- Verify SSID and password in `settings.toml`
- Ensure 2.4GHz network (5GHz not supported)
- Check WiFi signal strength
- Try reducing `WIFI_TIMEOUT` if network is slow

**Frequent Disconnects**
- Move closer to router
- Reduce API request frequency
- Check for network interference

### API Issues

**Invalid API Key**
- Verify key starts with `sk-ant-`
- Check for spaces or quotes in `settings.toml`
- Ensure API key has available credits
- Test key at console.anthropic.com

**Timeout Errors**
- Increase `API_TIMEOUT` (default 120s)
- Lower image quality mode
- Check internet connection speed
- Verify Claude API status

**Rate Limited**
- Wait 60 seconds between captures
- Check API tier limits at Anthropic console
- Increase `API_RETRY_DELAY`

### Image Issues

**Image Too Large**
- Switch to lower quality mode (MEDIUM or LOW)
- Reduce `CAMERA_RESOLUTION` setting
- Check `MAX_IMAGE_SIZE_KB` (default 3072)

**Blurry Photos**
- Use long-press SHUTTER for autofocus
- Ensure adequate lighting
- Clean camera lens
- Avoid camera shake during capture

**Dark Images**
- Enable `AUTO_FLASH_ENABLED = true`
- Adjust `DARK_THRESHOLD` (lower = more sensitive)
- Add manual lighting

### SD Card Issues

**No SD Card Detected**
- Ensure card is fully inserted
- Format as FAT32 (exFAT not supported)
- Try different SD card (some cards incompatible)
- Check card capacity (16GB-32GB recommended)

**Write Errors**
- Reformat SD card
- Check for corrupted filesystem
- Ensure card not write-protected
- Try slower write speed

### System Issues

**System Error / Crashes**
- Check serial console for error messages
- Verify all libraries installed correctly
- Ensure CircuitPython 10.x (not 9.x or 11.x)
- Try fresh CircuitPython installation

**Memory Errors**
- Reduce `CLAUDE_MAX_TOKENS`
- Lower image quality mode
- Restart device to clear memory

**Slow Performance**
- Check WiFi signal strength
- Reduce image size
- Clear SD card of old images
- Verify API response times

---

## Technical Details

### Architecture

**Main Components:**
- `Config` class - Centralized settings management
- `Logger` class - Structured logging
- `TextViewer` class - Scrollable response display
- Image utilities - Size checking, encoding, retrieval
- Camera utilities - Brightness detection, auto-flash
- Network utilities - WiFi connection, retry logic
- Claude API client - Image encoding, API communication

### Optimizations

**Memory Management:**
- 18 strategic `gc.collect()` calls
- Immediate `del` after large operations
- Base64 encoding with chunked cleanup

**Performance:**
- Fast image retrieval using mtime (not sorting)
- Integer math for brightness calculation (30*R + 59*G + 11*B / 100)
- 5-point brightness sampling (reduced from 9)
- Immediate feedback ("SNAP!") before processing

**Reliability:**
- Zero bare `except` blocks (100% specific exceptions)
- File existence validation before operations
- SD card health check on startup
- Comprehensive error recovery

### File Structure

Images saved as: `/sd/IMG_####.JPG` (sequential numbering)
Responses saved as: `/sd/IMG_PROMPTLABEL_####.TXT`

Example:
```
/sd/IMG_0001.JPG
/sd/IMG_DESCRIBE_0001.TXT
/sd/IMG_0002.JPG
/sd/IMG_HAIKU_0002.TXT
```

### API Communication

**Request Format:**
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 1024,
  "messages": [{
    "role": "user",
    "content": [
      {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}},
      {"type": "text", "text": "prompt here"}
    ]
  }]
}
```

**Response Parsing:**
Extracts `result["content"][0]["text"]` with validation at each level.

---

## Project Structure

```
cloudlens/
├── code.py              # Main application (1,200 lines)
├── settings.toml        # Complete configuration (all prompts & settings)
├── README.md            # This documentation
└── LICENSE              # MIT License with dual copyright
```

**Code Organization:**
- Lines 1-193: Configuration and logging
- Lines 194-289: Image and camera utilities
- Lines 290-323: Network utilities
- Lines 324-523: Claude API client
- Lines 524-698: Text viewer UI
- Lines 699-871: Display utilities
- Lines 872-1200: Main application loop

---

## Credits & Attribution

### Original Work
**"OpenAI Image Descriptors with Memento"**
Author: Liz Clark
Copyright: (c) 2024 Liz Clark for Adafruit Industries
Source: https://learn.adafruit.com/openai-image-descriptors-with-memento?view=all
License: MIT

### Derivative Work
**CloudLens**
Author: William Chesher
Copyright: (c) 2025 William Chesher
License: MIT

**Major Modifications:**
- Claude Vision API integration (replacing OpenAI)
- 12 specialized prompt modes with dynamic loading
- 4-tier quality mode system with size management
- Browse mode for saved image re-analysis
- Production-grade optimizations (memory, performance, reliability)
- Bulletproof error handling with specific exceptions
- Complete configuration externalization
- Professional UI with branding
- Comprehensive documentation

---

## License

**MIT License** — See LICENSE file for full text.

This project is a derivative work based on Adafruit's "OpenAI Image Descriptors with Memento" by Liz Clark, used under the MIT License. Both the original work and modifications are licensed under MIT.

**Original Copyright:** Copyright (c) 2024 Liz Clark for Adafruit Industries
**Derivative Copyright:** Copyright (c) 2025 William Chesher

---

## Version

**CloudLens 1.0 Production** - CircuitPython 10.x

**Release Notes:**
- Production-ready stability
- Zero bare exception blocks
- Strategic memory optimization
- Comprehensive error handling
- Professional UI with branding
- Full documentation

**Requirements:**
- CircuitPython 10.x (not 9.x or earlier)
- Anthropic API key with available credits
- 2.4GHz WiFi network
- FAT32 SD card
