# CloudLens: AI Vision Camera for CircuitPython

CloudLens is a CircuitPython 10.x camera application that integrates hardware cameras with Anthropic's Claude API for real-time AI vision analysis. Take a photo and get instant AI-powered responses with 12 creative prompt modes.

## Key Features

- **Real-Time AI Vision**: Capture photos and analyze them with Claude's vision capabilities
- **12 Creative Prompts**: Description, art analysis, haiku generation, translation, alien perspective, and more
- **Quality Modes**: LOW/MEDIUM/HIGH/ULTRA with automatic image size management
- **Auto-Flash**: Intelligent brightness detection for low-light photography
- **Scrollable Text Display**: Clean text viewer with multi-page navigation
- **Browse Mode**: Review and re-analyze previously captured images
- **Zero Hardcoded Values**: Complete configuration in `settings.toml`

## Hardware Requirements

- **Microcontroller**: Adafruit PyCamera S3 or similar CircuitPython 10.x compatible board
- **Camera**: Built-in camera module
- **Display**: 240×240 pixel display (built-in on PyCamera)
- **Storage**: SD card for image storage
- **WiFi**: Required for Claude API access

## Installation

1. **Flash CircuitPython 10.x** to your device
2. **Install required libraries** from the CircuitPython bundle:
   - `adafruit_pycamera`
   - `adafruit_requests`
   - `adafruit_display_text`
   - `jpegio`
3. **Copy files** to your CIRCUITPY drive:
   - `code.py`
   - `settings.toml`
4. **Configure** your `settings.toml`:
   ```toml
   CIRCUITPY_WIFI_SSID = "your-wifi-network"
   CIRCUITPY_WIFI_PASSWORD = "your-wifi-password"
   ANTHROPIC_API_KEY = "sk-ant-your-api-key-here"
   ```
5. **Reset** your device to start

## Configuration

All settings are in `settings.toml`:

### Network & API
```toml
CIRCUITPY_WIFI_SSID = "your-network"
CIRCUITPY_WIFI_PASSWORD = "your-password"
ANTHROPIC_API_KEY = "sk-ant-..."
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
```

### Camera & Quality
```toml
CAMERA_RESOLUTION = 3          # 0-6 (see comments in file)
DEFAULT_QUALITY_MODE = "MEDIUM"  # LOW, MEDIUM, HIGH, ULTRA
AUTO_FLASH_ENABLED = true
DARK_THRESHOLD = 30            # 0-255, brightness trigger
```

### Display
```toml
TEXT_SCALE = 2
TEXT_WRAP_WIDTH = 20
LINES_PER_PAGE = 7
```

### Prompt Modes
Define which prompts appear and in what order:
```toml
PROMPT_ORDER = "DESCRIBE,HAIKU,TRANSLATE,ALIEN,WEIRD,..."
```

Each prompt has a label and prompt text defined in settings.toml.

## Usage

### Controls

- **SHUTTER** (short press): Take photo & analyze
- **SHUTTER** (long press): Autofocus
- **LEFT/RIGHT**: Navigate prompts
- **UP/DOWN**: Change quality mode (or scroll text when viewing response)
- **SELECT**: Enter/exit browse mode
- **OK**: Close text view or send browsed image to Claude

### Quality Modes

| Mode | Resolution | Target Size | Use Case |
|------|------------|-------------|----------|
| LOW | 640×480 | ~300KB | Quick captures, conserve data |
| MEDIUM | 800×600 | ~600KB | Balanced quality/speed (default) |
| HIGH | 1024×768 | ~1000KB | Detailed analysis |
| ULTRA | 1280×720 | ~1400KB | Maximum detail |

### Prompt Modes

1. **DESCRIBE**: Accessibility-focused alt text descriptions
2. **ART ANALYSIS**: Formal art critique (line, shape, color, etc.)
3. **HAIKU**: Three-line poetry about the image
4. **TRANSLATE**: OCR and translation to English
5. **ALIEN**: Cute alien perspective on Earth items
6. **WEIRD**: Anomaly detection - anything unusual?
7. **MOVIE**: Sensational movie title and tagline
8. **PLANT**: Species identification
9. **CAR**: Imaginative automobile design
10. **DRAMA**: Soap opera storytelling
11. **STUDY BUDDY**: Educational tutoring for study materials
12. **KINDNESS**: Moments of human connection

## Customization

Add your own prompts to `settings.toml`:

```toml
CUSTOM_LABEL = "MY MODE"
CUSTOM_PROMPT = """Your custom instruction here..."""
```

Then add to the order:
```toml
PROMPT_ORDER = "DESCRIBE,CUSTOM,HAIKU,..."
```

## Project Structure

```
cloudlens/
├── code.py              # Main application (CircuitPython 10.x)
├── settings.toml        # All configuration (WiFi, API, prompts)
├── README.md            # This file
└── LICENSE              # MIT License
```

## Educational Use

CloudLens demonstrates:
- IoT hardware integration (camera, sensors, display)
- RESTful API communication with modern AI services
- Configuration management best practices
- Image processing and base64 encoding
- Error handling and retry logic
- User interface design for embedded devices

## Troubleshooting

**WiFi Connection Failed**
- Check SSID and password in settings.toml
- Ensure 2.4GHz WiFi (5GHz not supported)

**API Key Invalid**
- Verify key starts with `sk-ant-`
- Check for extra spaces or quotes

**Image Too Large**
- Lower quality mode (try MEDIUM or LOW)
- Check `MAX_IMAGE_SIZE_KB` setting (default 3072)

**No SD Card**
- Ensure SD card is properly inserted
- Format as FAT32 if necessary

## License

MIT License — see LICENSE file for details.

Copyright (c) 2025 William Chesher

## Version

CloudLens 1.0 Beta - CircuitPython 10.x
