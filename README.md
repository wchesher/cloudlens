# CloudLens: AI Vision Camera for CircuitPython

**Professional AI-powered camera system for microcontrollers.** CloudLens integrates hardware cameras with Anthropic's Claude Vision API for real-time image analysis. Capture photos and receive instant AI-powered insights through 12 specialized prompt modes with educational prompt engineering framework.

**Based on** [OpenAI Image Descriptors with Memento](https://learn.adafruit.com/openai-image-descriptors-with-memento?view=all) by Liz Clark for Adafruit Industries. Extensively modified for Claude Vision API with production-grade optimizations and features.

---

## Quick Start

**For experienced users:**

1. Flash CircuitPython 10.x to Adafruit Memento Camera Board
2. Install libraries: `adafruit_pycamera`, `adafruit_requests`, `adafruit_display_text`, `jpegio`
3. Copy `code.py` and `settings.toml` to CIRCUITPY drive
4. Edit `settings.toml`: Add WiFi credentials and Anthropic API key (`sk-ant-...`)
5. Insert FAT32-formatted SD card
6. Reset device and wait for "ready" message

**Controls:** SHUTTER (capture), LEFT/RIGHT (prompts), UP (toggle BRIEF/VERBOSE), DOWN (quality/scroll), SELECT (browse), OK (close/wake)

---

## Key Features

### Core Capabilities
- **Real-Time AI Vision**: Capture and analyze with Claude Sonnet 4.5
- **12 Educational Prompts**: Designed using professional prompt engineering framework
- **BRIEF/VERBOSE Toggle**: Smart response truncation with full-text on demand
- **Quality Rating System**: Prompts rated 1-3 stars for complexity and insight potential
- **4 Quality Modes**: LOW/MEDIUM/HIGH/ULTRA with automatic size management
- **Response Archiving**: Full responses automatically saved to SD card as `.txt` files

### Professional Features
- **Smart Auto-Flash**: 5-point brightness detection for low-light scenes
- **Browse Mode**: Review and re-analyze saved images with SELECT cancellation
- **Screensaver Mode**: Display turns off after 120 seconds of inactivity
- **Clean Boot Screen**: Branded loading animation with progress indicators
- **Scrollable Display**: Multi-page text viewer for long responses
- **Professional UI**: Branded viewfinder with dual quality indicators

### Technical Excellence
- **Zero Hardcoded Values**: 100% configuration via `settings.toml`
- **Production-Ready**: Bulletproof error handling, memory optimization, retry logic
- **Prompt Engineering Education**: 5-component framework teaches AI instruction design
- **Memory Optimized**: Strategic `gc.collect()` and immediate cleanup

---

## What's New in Version 1.0.0

### BRIEF/VERBOSE System
- **UP button toggles** between truncated (BRIEF) and full (VERBOSE) text
- Smart truncation respects prompt types (haiku never truncated)
- Full responses always saved to SD card as `.txt` files
- Visual indicator shows current mode: `[B]` or `[V]`

### Prompt Engineering Framework
All 12 prompts redesigned using 5-component structure:
1. **ROLE** - Who is the AI? (expertise, perspective)
2. **ATTITUDE** - How do they communicate? (tone, personality)
3. **TASK** - What's the core objective? (clear action)
4. **CONSTRAINTS** - What are the boundaries? (rules, limits)
5. **OUTPUT FORMAT** - How is it structured? (exact format)

### Quality Rating System
- Prompts rated 1-3 stars based on complexity and insight potential
- **⭐ (Quality 1)**: Straightforward tasks (DESCRIBE, TRANSLATE, PLANT_ID, WEIRD)
- **⭐⭐ (Quality 2)**: Creative interpretation (HAIKU, MOVIE, ALIEN, CAR)
- **⭐⭐⭐ (Quality 3)**: Deep analysis (ART_ANALYSIS, STUDY, KINDNESS, DRAMA)
- Stars displayed in lower-right corner (gold, scale=2)

### UI Enhancements
- **Clean boot screen**: Loading animation with animated dots
- **Screensaver mode**: Display turns off after 120s inactivity (any button wakes)
- **Improved feedback**: "snap" instead of "SNAP!" for refined aesthetic
- **Dual quality display**: Image quality (upper-right), prompt quality (lower-right)

---

## Hardware Requirements

### Primary Hardware
**Adafruit Memento Camera Board** - ESP32-S3 based AI camera platform
- **Product**: [Adafruit Memento Camera](https://www.adafruit.com/product/5420)
- **Guide**: [Adafruit Memento Learning Guide](https://learn.adafruit.com/adafruit-memento-camera-board?view=all)
- **CircuitPython**: [Memento CircuitPython Page](https://circuitpython.org/board/adafruit_esp32s3_camera/)

### Required Components
- **Microcontroller**: Adafruit Memento Camera Board (ESP32-S3 based)
- **Camera Module**: OV5640 5-megapixel camera (built-in)
- **Display**: 240×240 pixel round TFT (built-in)
- **SD Card**: Any size, FAT32 formatted
- **WiFi**: 2.4GHz network access
- **Power**: USB-C or LiPo battery (500mA recommended)

### Recommended Accessories
- **Enclosure**: [Memento Enclosure with LED Ring Flash](https://www.adafruit.com/product/5843)
- **SD Card**: Class 10, 16-32GB recommended for faster writes
- **WiFi**: Strong signal for reliable API calls
- **Anthropic API**: Active API key with credits
- **Battery**: 3.7V LiPo for portable operation

### Compatible Hardware
This code also works with:
- Adafruit PyCamera S3 (uses same `adafruit_pycamera` library)
- Any ESP32-S3 board with OV5640 camera using the PyCamera library

---

## Installation

### 1. Flash CircuitPython 10.x
Download and install CircuitPython 10.x for Adafruit Memento from the [Memento CircuitPython page](https://circuitpython.org/board/adafruit_esp32s3_camera/)

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
Format SD card as FAT32, insert into Memento Camera Board

### 6. Reset Device
Press reset button or reconnect USB. Wait for "ready" message on display.

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
CLAUDE_MAX_TOKENS = "1024"
```

**Camera & Quality:**
```toml
CAMERA_RESOLUTION = "3"              # 0-12 (3 = 800×600)
DEFAULT_QUALITY_MODE = "MEDIUM"      # LOW, MEDIUM, HIGH, ULTRA
AUTO_FLASH_ENABLED = "true"
DARK_THRESHOLD = "30"                # 0-255, lower = more sensitive
```

**Response Display:**
```toml
DEFAULT_VERBOSITY = "BRIEF"          # Start with BRIEF or VERBOSE
SAVE_FULL_RESPONSES = "true"         # Save .txt files to SD
BRIEF_MODE_LIMIT = "200"             # Character limit for BRIEF
```

**Screensaver:**
```toml
SCREENSAVER_TIMEOUT = "120"          # Seconds (0 to disable)
```

**Display:**
```toml
TEXT_SCALE = "2"                     # Font size multiplier
TEXT_WRAP_WIDTH = "20"               # Characters per line
LINES_PER_PAGE = "7"                 # Lines visible per screen
```

**Network Tuning:**
```toml
WIFI_TIMEOUT = "30"                  # Seconds
WIFI_RETRY_ATTEMPTS = "3"
API_TIMEOUT = "120"                  # Seconds
API_RETRY_ATTEMPTS = "3"
API_RETRY_DELAY = "2"                # Seconds between retries
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
| **UP** | Toggle/Quality | Toggle BRIEF/VERBOSE when viewing text, change quality in viewfinder |
| **DOWN** | Scroll/Quality | Scroll down when viewing text, change quality in viewfinder |
| **SELECT** | Browse/Cancel | Enter/exit saved image browser, cancel API calls |
| **OK** | Confirm/Wake | Send browsed image, close text viewer, wake from screensaver |

### Viewfinder Display

```
┌─────────────────────────────────────┐
│ CloudLens              ** MED 800p  │ ← Branding + Image Quality
│                                     │
│         [LIVE VIEWFINDER]           │
│                                     │
│                                     │
│  DESCRIBE                       *** │ ← Prompt Mode + Quality Stars
└─────────────────────────────────────┘
```

**Display Elements:**
- **Top-left**: CloudLens branding (green)
- **Top-right**: Image quality mode with icon (cyan) - e.g., "** MED 800p"
- **Bottom-left**: Current prompt mode (cyan, large) - e.g., "DESCRIBE"
- **Bottom-right**: Prompt quality stars (gold, large) - ⭐, ⭐⭐, or ⭐⭐⭐

### Quality Modes

| Mode | Resolution | Target Size | Max Expected | Use Case |
|------|------------|-------------|--------------|----------|
| **LOW** | 640×480 | 300 KB | 450 KB | Quick captures, data conservation |
| **MEDIUM** | 800×600 | 600 KB | 800 KB | Balanced quality/speed (default) |
| **HIGH** | 1024×768 | 1000 KB | 1400 KB | Detailed analysis |
| **ULTRA** | 1280×720 | 1400 KB | 2000 KB | Maximum detail, fine print |

**Note:** Images exceeding 3 MB will be rejected with error message.

### Prompt Modes

All prompts use the 5-component framework (ROLE, ATTITUDE, TASK, CONSTRAINTS, OUTPUT FORMAT):

**Quality 1 (⭐) - Straightforward Tasks:**
1. **DESCRIBE** - Accessibility specialist writing alt text for screen readers
2. **TRANSLATE** - Translator converting non-English text to English
3. **PLANT_ID** - Botanist identifying plant species with scientific nomenclature
4. **WEIRD** - Observer detecting unusual, unexpected, or odd elements

**Quality 2 (⭐⭐) - Creative Interpretation:**
5. **HAIKU** - Contemplative poet composing 5-7-5 haiku about the image
6. **MOVIE** - Hollywood pitch writer creating sensational movie titles
7. **ALIEN** - Confused alien visitor experiencing Earth for the first time
8. **CAR** - Automotive designer imagining objects as fictional car concepts

**Quality 3 (⭐⭐⭐) - Deep Analysis:**
9. **ART_ANALYSIS** - Art educator analyzing 7 formal elements (LINE, SHAPE, COLOR, TEXTURE, SPACE, BALANCE, EMPHASIS)
10. **STUDY** - Patient tutor creating practice questions, mnemonics, and real-world applications
11. **KINDNESS** - Documentarian exploring moments of human connection and compassion
12. **DRAMA** - Melodramatic soap opera writer creating peak cliffhanger scenes

### Workflow

1. **Power On** → Watch clean boot animation with "Loading....." dots
2. **Wait** → "ready" message appears, viewfinder starts
3. **Select Prompt** → LEFT/RIGHT to choose mode (see quality stars change)
4. **Adjust Quality** → UP/DOWN for resolution
5. **Compose Shot** → Frame your subject
6. **Capture** → Press SHUTTER
7. **Wait** → "snap" → "Sending to Claude..." (SELECT to cancel)
8. **Read Response** → Starts in BRIEF mode
9. **Toggle Detail** → Press UP to expand to VERBOSE, UP again to collapse
10. **Scroll** → DOWN to scroll through text
11. **Close** → OK to return to viewfinder
12. **Browse** → SELECT to review saved images

### BRIEF/VERBOSE Toggle

**BRIEF Mode (Default):**
- Shows 1-2 sentences or first key point (~200 characters)
- Quick scan for essential information
- Prompts like HAIKU, PLANT_ID always show full text
- Displays `[B] UP=toggle OK=close` at bottom

**VERBOSE Mode:**
- Shows complete response
- Full detail for deep analysis
- Press UP again to return to BRIEF
- Displays `[V] UP=toggle OK=close` at bottom

**Example with ART_ANALYSIS (⭐⭐⭐):**
```
BRIEF: "This artwork uses curved lines and warm colors creating visual movement..."
       [↑ UP for full response]

       ↓ Press UP

VERBOSE: "LINE: The composition features flowing curved lines creating dynamic
          movement throughout...
          SHAPE: Organic shapes dominate with soft edges...
          COLOR: Warm palette with reds, oranges, and yellows...
          [full 7-element analysis]"
```

### Screensaver Mode

**Activation:**
- After 120 seconds of no button presses (configurable)
- Screen completely blacks out (backlight OFF)
- Saves battery and extends LCD lifespan

**Wake-Up:**
- Press any button to turn screen back on
- Activity timer resets
- First button press is consumed (prevents accidental photo)

**Configuration:**
- Set `SCREENSAVER_TIMEOUT = "0"` to disable
- Adjust timeout: `SCREENSAVER_TIMEOUT = "300"` for 5 minutes

---

## Customization

### Adding Custom Prompts

CloudLens prompts follow a 5-component structure for educational consistency:

1. **Define your prompt** in `settings.toml`:
```toml
MYMODE_LABEL = "DETECTIVE"
MYMODE_QUALITY = "3"
MYMODE_PROMPT = "ROLE: You are a detective investigating a crime scene.\n\nATTITUDE: Your analysis is methodical, detail-oriented, and evidence-focused.\n\nTASK: Analyze this image as if it were a crime scene, identifying key details and evidence.\n\nCONSTRAINTS:\n- Focus on observable facts, not speculation\n- Note positions, conditions, and relationships of objects\n- Identify potential evidence or anomalies\n- Keep analysis structured and professional\n\nOUTPUT FORMAT:\nEVIDENCE: [list key observations]\nANOMALIES: [unusual elements]\nTHEORY: [logical interpretation]"
```

2. **Add to prompt order**:
```toml
PROMPT_ORDER = "DESCRIBE,MYMODE,ART_ANALYSIS,..."
```

3. **Reset device** to load new prompt

**Prompt Engineering Tips:**
- **ROLE**: Establishes expertise and perspective
- **ATTITUDE**: Sets tone (formal, playful, analytical)
- **TASK**: Clear, specific instruction
- **CONSTRAINTS**: Rules prevent off-topic responses
- **OUTPUT FORMAT**: Structure makes parsing easier

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

**Stuck at "Sending to Claude"**
- Press SELECT button to cancel API call
- Increase `API_TIMEOUT` (default 120s)
- Check internet connection speed
- Verify Claude API status

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

### Display Issues

**Mode Indicator Not Showing**
- Prompt mode should appear in lower-left corner
- Check that `_botbar` is visible
- Reset device if UI elements missing

**Screensaver Won't Activate**
- Check `SCREENSAVER_TIMEOUT` in settings.toml
- Ensure value is greater than 0
- Verify 120 seconds of complete inactivity

**Screensaver Won't Wake**
- Press OK button firmly
- Try other buttons (shutter, select)
- Check for hardware button issues

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
- `Config` class - Centralized settings management with quality ratings
- `Logger` class - Structured logging
- `TextViewer` class - Scrollable response display with BRIEF/VERBOSE toggle
- Image utilities - Size checking, encoding, retrieval
- Camera utilities - Brightness detection, auto-flash
- Network utilities - WiFi connection, retry logic
- Claude API client - Image encoding, API communication with cancellation
- Loading screen - Clean boot animation
- Screensaver - Power management

### Optimizations

**Memory Management:**
- Strategic `gc.collect()` calls throughout code
- Immediate `del` after large operations
- Base64 encoding with chunked cleanup

**Performance:**
- Fast image retrieval using mtime (not sorting)
- Integer math for brightness calculation (30*R + 59*G + 11*B / 100)
- 5-point brightness sampling (reduced from 9)
- Immediate feedback ("snap") before processing
- Smart truncation caches both BRIEF and VERBOSE in memory

**Reliability:**
- Zero bare `except` blocks (100% specific exceptions)
- File existence validation before operations
- SD card health check on startup
- Comprehensive error recovery
- SELECT button cancellation during API calls

### File Structure

Images saved as: `/sd/IMG_####.JPG` (sequential numbering)
Responses saved as: `/sd/IMG_####_response.txt`

Example:
```
/sd/IMG_0001.JPG
/sd/IMG_0001_response.txt
/sd/IMG_0002.JPG
/sd/IMG_0002_response.txt
```

**Response File Format:**
```
Prompt: DESCRIBE
Image: /sd/IMG_0001.JPG
----------------------------------------

[Full response text here]
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

### Prompt Engineering Framework

CloudLens uses a structured 5-component prompt design that teaches effective AI instruction:

**Component Breakdown:**
1. **ROLE**: Establishes AI expertise and perspective (e.g., "art educator", "botanist")
2. **ATTITUDE**: Sets communication tone (e.g., "precise and pedagogical", "playfully confused")
3. **TASK**: Clear, specific objective (e.g., "Analyze using 7 formal elements")
4. **CONSTRAINTS**: Boundaries and rules (e.g., "2-3 sentences", "ignore image quality")
5. **OUTPUT FORMAT**: Exact structure specification (e.g., "LINE: [observation]")

**Educational Value:**
- Students learn prompt engineering by studying working examples
- Quality ratings (1-3) demonstrate complexity levels
- Each prompt is a self-contained lesson in AI instruction
- Modifications teach how prompt components affect responses

---

## Project Structure

```
cloudlens/
├── code.py              # Main application (~1,600 lines)
├── settings.toml        # Complete configuration (all prompts & settings)
├── README.md            # This documentation
└── LICENSE              # MIT License with dual copyright
```

**Code Organization:**
- Lines 1-210: Configuration, logging, and utilities
- Lines 211-463: Image and camera utilities
- Lines 464-576: Claude API client with cancellation
- Lines 577-930: Text viewer UI with BRIEF/VERBOSE toggle
- Lines 931-1055: Display utilities and loading screen
- Lines 1056-1134: Boot screen and screensaver functions
- Lines 1135-1650: Main application loop

---

## Credits & Attribution

### Original Work
**"OpenAI Image Descriptors with Memento"**
- Author: Liz Clark
- Copyright: (c) 2024 Liz Clark for Adafruit Industries
- Source: https://learn.adafruit.com/openai-image-descriptors-with-memento?view=all
- License: MIT

### Derivative Work
**CloudLens**
- Author: William Chesher
- Copyright: (c) 2025 William Chesher
- License: MIT

**Major Modifications:**
- Claude Vision API integration (replacing OpenAI)
- 12 specialized prompt modes with educational framework
- BRIEF/VERBOSE toggle system with smart truncation
- Prompt engineering framework (ROLE, ATTITUDE, TASK, CONSTRAINTS, OUTPUT FORMAT)
- Quality rating system (1-3 stars) for prompts
- 4-tier quality mode system with size management
- Response archiving to SD card (.txt files)
- Browse mode for saved image re-analysis
- Screensaver mode with 120-second timeout
- Clean boot screen with loading animation
- SELECT button API cancellation
- Production-grade optimizations (memory, performance, reliability)
- Bulletproof error handling with specific exceptions
- Complete configuration externalization
- Professional UI with dual quality indicators
- Comprehensive documentation

---

## License

**MIT License** — See LICENSE file for full text.

This project is a derivative work based on Adafruit's "OpenAI Image Descriptors with Memento" by Liz Clark, used under the MIT License. Both the original work and modifications are licensed under MIT.

**Original Copyright:** Copyright (c) 2024 Liz Clark for Adafruit Industries
**Derivative Copyright:** Copyright (c) 2025 William Chesher

---

## Version

**CloudLens 1.0.0** - CircuitPython 10.x Production Release

**Release Highlights:**
- BRIEF/VERBOSE toggle system for smart response display
- Educational prompt engineering framework (5 components)
- Quality rating system (1-3 stars) for prompt complexity
- Response archiving to SD card (.txt files)
- Screensaver mode (120-second timeout)
- Clean boot screen with loading animation
- SELECT button API cancellation support
- Production-ready stability
- Zero bare exception blocks
- Strategic memory optimization
- Comprehensive error handling
- Professional UI with dual quality indicators
- Full documentation

**Requirements:**
- CircuitPython 10.x (not 9.x or earlier)
- Anthropic API key with available credits
- 2.4GHz WiFi network
- FAT32 SD card

**Educational Use:**
CloudLens is designed as a teaching tool for prompt engineering and AI literacy. Each prompt demonstrates professional AI instruction design using the 5-component framework. Students can study, modify, and experiment with prompts to learn effective AI communication.

---

**Built with ❤️ for AI education and creative exploration**
