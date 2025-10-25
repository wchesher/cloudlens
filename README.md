# CloudLens: AI Vision for CircuitPython

CloudLens is a CircuitPython-based AI vision system that integrates camera hardware with Anthropic's Claude API. Designed for educational use, IoT development, and real-world AI applications, it demonstrates best practices in configuration management, API integration, and embedded systems design.

## Key Features

- **AI Vision Analysis**: Real-time image analysis using Claude's vision capabilities
- **Multiple Prompt Modes**: 12 pre-configured analysis modes (accessibility descriptions, art analysis, haiku generation, OCR/translation, and more)
- **Zero Hardcoded Values**: Complete separation of code, settings, and secrets
- **Network Resilience**: Automatic retry logic and graceful error handling
- **Modular Architecture**: Clean separation of concerns with reusable components
- **Auto-Flash Support**: Optional light sensor integration for low-light photography
- **Educational Focus**: Teaches IoT, API integration, and software architecture concepts

## Hardware Requirements

- **Microcontroller**: CircuitPython-compatible board with WiFi (ESP32-S3 recommended)
- **Camera Module**: Compatible with your microcontroller
- **Optional**: Light sensor for auto-flash functionality
- **Optional**: Display (240×240 recommended for visual feedback)

⚠️ Ensure your board supports WiFi and has sufficient memory for HTTPS requests and image processing.

## Installation Steps

1. **Flash CircuitPython 9.0+** to your microcontroller
2. **Install required libraries** from the CircuitPython bundle (see `requirements.txt`)
3. **Copy project files** to your CIRCUITPY drive:
   - `code.py` (main application)
   - `settings.toml` (configuration)
   - `secrets.toml` (from `secrets.toml.example`)
   - `lib/` directory (settings loader and dependencies)
4. **Configure credentials** in `secrets.toml`:
   ```toml
   CIRCUITPY_WIFI_SSID = "your-network"
   CIRCUITPY_WIFI_PASSWORD = "your-password"
   ANTHROPIC_API_KEY = "sk-ant-api03-..."
   ```
5. **Customize settings** in `settings.toml` as needed
6. **Reset your device** to start the application

## Configuration

CloudLens uses TOML configuration files to separate concerns:

- **`secrets.toml`**: WiFi credentials and API keys (never committed to git)
- **`settings.toml`**: All application settings (camera, prompts, network, API)
- **`code.py`**: Business logic only (no hardcoded values)

### Camera Settings

```toml
[camera]
resolution = 1  # 0-6 (0=240×240, 1=320×240, etc.)
```

### Flash Settings

```toml
[flash]
auto_flash_enabled = true
dark_threshold = 30  # 0-255, lower = darker conditions needed
```

### API Settings

```toml
[api]
model = "claude-3-5-sonnet-20241022"
max_tokens = 1024
timeout = 30
```

## Prompt Modes

CloudLens includes 12 creative AI prompt modes:

| Mode | Purpose | Educational Focus |
|------|---------|-------------------|
| **DESCRIBE** | Accessibility descriptions | Social media accessibility, alt text |
| **ART ANALYSIS** | Formal art critique | Art education, critical thinking |
| **HAIKU** | Creative poetry | Constraint-based generation |
| **TRANSLATE** | OCR and translation | Computer vision + NLP |
| **ALIEN** | Perspective-shifting descriptions | Creative thinking |
| **WEIRD** | Anomaly detection | Context understanding |
| **MOVIE** | Title and tagline generation | Creative AI, marketing |
| **PLANT** | Species identification | Classification tasks |
| **CAR** | Product design ideas | Creative reasoning |
| **DRAMA** | Soap opera storytelling | Creative writing |
| **STUDY** | Educational tutoring | Interactive learning |
| **KINDNESS** | Social-emotional observation | AI ethics |

### Custom Prompts

Add your own prompt to `settings.toml`:

```toml
[prompts.CUSTOM]
label = "MY MODE"
prompt = """Your custom instruction here..."""
```

Then add it to the prompt order:
```toml
[prompts]
order = "DESCRIBE,CUSTOM,..."
```

## Architectural Highlights

- **Configuration as Code**: All settings externalized to TOML files
- **Separation of Concerns**: Code, settings, and secrets completely separated
- **Fail-Fast Validation**: Early detection of configuration errors
- **Network Resilience**: Retry logic with exponential backoff
- **Modular Design**: Reusable settings loader and clean function architecture

## Learning Outcomes

Students gain hands-on experience with:
- RESTful API integration and authentication
- Image processing and base64 encoding
- IoT hardware interfacing (cameras, sensors, displays)
- Configuration management and security best practices
- Error handling and resilient system design
- Prompt engineering for AI applications

## Educational Applications

CloudLens serves as a teaching tool for:
- Computer science and IoT courses
- AI and machine learning introduction
- Software engineering best practices
- Creative computing and digital art
- Accessibility technology
- Embedded systems development

## Project Structure

```
cloudlens/
├── code.py                    # Main application (no hardcoded values)
├── settings.toml              # All configuration settings
├── secrets.toml               # Credentials (NOT in git)
├── secrets.toml.example       # Template for secrets
├── lib/
│   └── settings_loader.py     # Settings management utility
├── requirements.txt           # CircuitPython library dependencies
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## License

MIT License — see LICENSE file for details.

Copyright (c) 2025 William Chesher
