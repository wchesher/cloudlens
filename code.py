# SPDX-FileCopyrightText: 2024 Liz Clark for Adafruit Industries
# SPDX-FileCopyrightText: 2025 William Chesher
# SPDX-License-Identifier: MIT
#
# Based on "OpenAI Image Descriptors with Memento" by Liz Clark
# Original: https://learn.adafruit.com/openai-image-descriptors-with-memento?view=all
# Modified for Claude Vision API and extensive feature additions
"""
CloudLens - AI Camera with Claude Vision API
CircuitPython 10.x compatible - Version 1.0 Production

Derived from Adafruit's OpenAI Image Descriptors project by Liz Clark
Modified to use Claude Vision API with extensive optimizations and features

All configuration is in settings.toml - NO hardcoded values

OPTIMIZATIONS:
- Specific exception handling (no bare except blocks)
- Strategic gc.collect() and del for memory management
- Consolidated duplicate code blocks
- SD card validation at startup
- File existence checks before encoding
- Optimized brightness check (5 points, integer math)
- Memory cleanup after large operations
- Bulletproof error handling throughout
"""

import os
import time
import ssl
import binascii
import gc
import wifi
import vectorio
import socketpool
import adafruit_requests
import displayio
from jpegio import JpegDecoder
from adafruit_display_text import label, wrap_text_to_lines
import terminalio
import adafruit_pycamera

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration management - ALL values from settings.toml"""

    # Credentials
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    WIFI_SSID = os.getenv("CIRCUITPY_WIFI_SSID")
    WIFI_PASSWORD = os.getenv("CIRCUITPY_WIFI_PASSWORD")

    # Claude API Settings
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
    CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "1024"))
    CLAUDE_API_VERSION = os.getenv("CLAUDE_API_VERSION", "2023-06-01")
    CLAUDE_ENDPOINT = os.getenv("CLAUDE_ENDPOINT", "https://api.anthropic.com/v1/messages")

    # Network settings
    WIFI_TIMEOUT = int(os.getenv("WIFI_TIMEOUT", "30"))
    WIFI_RETRY_ATTEMPTS = int(os.getenv("WIFI_RETRY_ATTEMPTS", "3"))
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "120"))
    API_RETRY_ATTEMPTS = int(os.getenv("API_RETRY_ATTEMPTS", "3"))
    API_RETRY_DELAY = int(os.getenv("API_RETRY_DELAY", "2"))

    # Display settings
    TEXT_SCALE = int(os.getenv("TEXT_SCALE", "2"))
    TEXT_WRAP_WIDTH = int(os.getenv("TEXT_WRAP_WIDTH", "20"))
    LINES_PER_PAGE = int(os.getenv("LINES_PER_PAGE", "7"))
    TEXT_Y_POSITION = int(os.getenv("TEXT_Y_POSITION", "20"))
    MSG_DURATION = float(os.getenv("MSG_DURATION", "0.5"))

    # Auto-flash settings
    AUTO_FLASH_ENABLED = os.getenv("AUTO_FLASH_ENABLED", "true").lower() == "true"
    DARK_THRESHOLD = int(os.getenv("DARK_THRESHOLD", "30"))

    # Camera settings
    CAMERA_RESOLUTION = int(os.getenv("CAMERA_RESOLUTION", "3"))
    DEFAULT_QUALITY_MODE = os.getenv("DEFAULT_QUALITY_MODE", "MEDIUM")
    MAX_IMAGE_SIZE_KB = int(os.getenv("MAX_IMAGE_SIZE_KB", "3072"))

    # Quality modes - read from settings.toml flat structure
    @classmethod
    def _load_quality_mode(cls, mode_name):
        """Load a single quality mode from settings.toml"""
        prefix = f"quality_{mode_name}_"
        return {
            "resolution": int(os.getenv(f"{prefix}resolution", "3")),
            "label": os.getenv(f"{prefix}label", mode_name),
            "target_kb": int(os.getenv(f"{prefix}target_kb", "600")),
            "max_expected_kb": int(os.getenv(f"{prefix}max_expected_kb", "800")),
            "icon": os.getenv(f"{prefix}icon", "*")
        }

    @classmethod
    def get_quality_modes(cls):
        """Get quality modes configuration"""
        return {
            "LOW": cls._load_quality_mode("LOW"),
            "MEDIUM": cls._load_quality_mode("MEDIUM"),
            "HIGH": cls._load_quality_mode("HIGH"),
            "ULTRA": cls._load_quality_mode("ULTRA")
        }

    QUALITY_MODES = None  # Will be loaded dynamically
    QUALITY_MODE_ORDER = ["LOW", "MEDIUM", "HIGH", "ULTRA"]

    # Resolution mapping for display
    RESOLUTION_MAP = {
        0: "240x240", 1: "320x240", 2: "640x480", 3: "800x600",
        4: "1024x768", 5: "1280x720", 6: "1280x1024", 7: "1600x1200",
        8: "1920x1080", 9: "2048x1536", 10: "2560x1440", 11: "2560x1600",
        12: "2560x1920"
    }

    @classmethod
    def validate_camera_resolution(cls):
        """Validate and log camera resolution"""
        if cls.CAMERA_RESOLUTION in cls.RESOLUTION_MAP:
            print(f"[INFO] Camera resolution: {cls.CAMERA_RESOLUTION} = {cls.RESOLUTION_MAP[cls.CAMERA_RESOLUTION]}")
        else:
            print(f"[WARN] Invalid resolution {cls.CAMERA_RESOLUTION}, using default 3")
            cls.CAMERA_RESOLUTION = 3

        return cls.CAMERA_RESOLUTION

    @classmethod
    def get_resolution_string(cls, resolution_code):
        """Get resolution string for display"""
        return cls.RESOLUTION_MAP.get(resolution_code, "???x???")

    @classmethod
    def get_quality_mode_info(cls, mode_name):
        """Get quality mode configuration"""
        if cls.QUALITY_MODES is None:
            cls.QUALITY_MODES = cls.get_quality_modes()
        return cls.QUALITY_MODES.get(mode_name, cls.QUALITY_MODES["MEDIUM"])

    @classmethod
    def validate_quality_mode(cls, mode_name):
        """Validate quality mode exists"""
        if mode_name not in cls.QUALITY_MODE_ORDER:
            print(f"[WARN] Invalid quality mode '{mode_name}', using MEDIUM")
            return "MEDIUM"
        return mode_name

    PROMPT_ORDER = os.getenv("PROMPT_ORDER")

    @classmethod
    def get_prompts(cls):
        """Dynamically load ALL prompts from settings.toml"""
        prompts = []
        labels = []

        prompt_order = cls.PROMPT_ORDER

        if not prompt_order:
            print("[ERROR] PROMPT_ORDER not found in settings.toml")
            return [], []

        prompt_names = [name.strip() for name in prompt_order.split(',')]
        print(f"[INFO] Loading {len(prompt_names)} prompts...")

        for prompt_name in prompt_names:
            prompt_var = f"{prompt_name}_PROMPT"
            label_var = f"{prompt_name}_LABEL"

            prompt_text = os.getenv(prompt_var)
            label_text = os.getenv(label_var)

            if prompt_text:
                prompts.append(prompt_text)
                labels.append(label_text if label_text else prompt_name)
                print(f"[INFO]   ✓ {prompt_name}")
            else:
                print(f"[WARN]   ✗ {prompt_var} not found")

        return prompts, labels

    @classmethod
    def validate(cls):
        """Validate configuration"""
        issues = []

        if not cls.WIFI_SSID or not cls.WIFI_PASSWORD:
            issues.append("WiFi credentials missing")

        if not cls.ANTHROPIC_API_KEY:
            issues.append("ANTHROPIC_API_KEY missing")
        elif not cls.ANTHROPIC_API_KEY.startswith("sk-ant-"):
            issues.append("Invalid ANTHROPIC_API_KEY format")

        prompts, labels = cls.get_prompts()
        if len(prompts) == 0:
            issues.append("No prompts found in settings.toml")

        return issues

# ============================================================================
# SIMPLE LOGGER
# ============================================================================

class Logger:
    """Lightweight logging"""

    @staticmethod
    def info(msg, *args):
        print(f"[INFO] {msg.format(*args) if args else msg}")

    @staticmethod
    def warn(msg, *args):
        print(f"[WARN] {msg.format(*args) if args else msg}")

    @staticmethod
    def error(msg, *args):
        print(f"[ERROR] {msg.format(*args) if args else msg}")

logger = Logger()

# ============================================================================
# IMAGE UTILITIES
# ============================================================================

def get_file_size_kb(filepath):
    """Get file size in KB"""
    try:
        stat = os.stat(filepath)
        return stat[6] / 1024
    except (OSError, AttributeError):
        return 0

def check_image_size(filepath, mode_info):
    """Check if captured image is within acceptable size"""
    size_kb = get_file_size_kb(filepath)

    if size_kb > Config.MAX_IMAGE_SIZE_KB:
        return False, int(size_kb), f"TOO LARGE! {int(size_kb)}KB > 3MB"

    max_expected = mode_info.get("max_expected_kb", mode_info["target_kb"] * 1.5)

    if size_kb > max_expected:
        return True, int(size_kb), f"Larger than expected: {int(size_kb)}KB"
    elif size_kb > mode_info["target_kb"] * 1.2:
        return True, int(size_kb), f"Good: {int(size_kb)}KB"
    else:
        return True, int(size_kb), f"Perfect: {int(size_kb)}KB"

# ============================================================================
# CAMERA UTILITIES
# ============================================================================

def check_brightness(pycam):
    """Check if scene is too dark and needs flash"""
    try:
        frame = None
        for attempt in range(2):
            frame = pycam.continuous_capture()
            if frame and hasattr(frame, 'width') and hasattr(frame, 'height'):
                break
            if attempt == 0:
                time.sleep(0.1)

        if not frame or not hasattr(frame, 'width') or not hasattr(frame, 'height'):
            return False

        width = frame.width
        height = frame.height

        if width < 8 or height < 8:
            return False

        # Sample 5 key points for speed (center + 4 quadrants)
        sample_points = [
            (width // 2, height // 2),      # Center
            (width // 4, height // 4),      # Top-left
            (3 * width // 4, height // 4),  # Top-right
            (width // 4, 3 * height // 4),  # Bottom-left
            (3 * width // 4, 3 * height // 4),  # Bottom-right
        ]

        total_brightness = 0

        for x, y in sample_points:
            pixel = frame[x, y]
            # Extract RGB using bit shifts
            r = ((pixel >> 11) & 0x1F) << 3
            g = ((pixel >> 5) & 0x3F) << 2
            b = (pixel & 0x1F) << 3
            # Use integer approximation: (30*r + 59*g + 11*b) / 100
            brightness = (30 * r + 59 * g + 11 * b) // 100
            total_brightness += brightness

        avg_brightness = total_brightness // len(sample_points)
        is_dark = avg_brightness < Config.DARK_THRESHOLD

        # Free frame memory
        del frame
        gc.collect()

        if is_dark:
            logger.info("Scene is dark (brightness: {}) - flash recommended", avg_brightness)
        else:
            logger.info("Scene brightness OK: {}", avg_brightness)

        return is_dark

    except Exception as e:
        logger.error("Brightness check failed: {}", e)
        return False

# ============================================================================
# NETWORK UTILITIES
# ============================================================================

def connect_wifi(ssid=None, password=None):
    """Connect to WiFi with retry logic"""
    ssid = ssid or Config.WIFI_SSID
    password = password or Config.WIFI_PASSWORD

    if not ssid or not password:
        logger.error("WiFi credentials not configured")
        return None

    logger.info("Connecting to WiFi: {}", ssid)

    for attempt in range(1, Config.WIFI_RETRY_ATTEMPTS + 1):
        try:
            if wifi.radio.connected:
                wifi.radio.stop_station()
                time.sleep(0.5)

            wifi.radio.connect(ssid, password, timeout=Config.WIFI_TIMEOUT)

            if wifi.radio.connected:
                logger.info("WiFi connected! IP: {}", wifi.radio.ipv4_address)
                pool = socketpool.SocketPool(wifi.radio)
                return adafruit_requests.Session(pool, ssl.create_default_context())

        except Exception as e:
            logger.warn("WiFi attempt {}/{} failed: {}", attempt, Config.WIFI_RETRY_ATTEMPTS, e)
            if attempt < Config.WIFI_RETRY_ATTEMPTS:
                time.sleep(2)

    logger.error("WiFi connection failed")
    return None

# ============================================================================
# CLAUDE API CLIENT
# ============================================================================

def encode_image(image_path):
    """Encode image to base64"""
    try:
        # Validate file exists first
        try:
            os.stat(image_path)
        except OSError:
            logger.error("Image file not found: {}", image_path)
            return None

        with open(image_path, 'rb') as f:
            data = f.read()

        file_size = len(data)

        if file_size > 5242880:
            logger.error("Image too large: {} bytes (max 5MB)", file_size)
            del data
            return None

        base64_data = binascii.b2a_base64(data).decode('utf-8').rstrip()
        del data  # Free memory immediately
        gc.collect()

        if len(base64_data) > 7000000:
            logger.error("Encoded image too large: {} bytes", len(base64_data))
            del base64_data
            return None

        return base64_data
    except Exception as e:
        logger.error("Encode failed: {}", e)
        return None

def send_to_claude(requests_session, image_path, prompt, prompt_label):
    """Send image to Claude API"""
    if not requests_session:
        return False, "Error: No network"

    if not Config.ANTHROPIC_API_KEY:
        return False, "Error: No API key"

    base64_image = encode_image(image_path)
    if not base64_image:
        return False, "Error: Image too large or encoding failed"

    headers = {
        "anthropic-version": Config.CLAUDE_API_VERSION,
        "content-type": "application/json",
        "x-api-key": Config.ANTHROPIC_API_KEY
    }

    payload = {
        "model": Config.CLAUDE_MODEL,
        "max_tokens": Config.CLAUDE_MAX_TOKENS,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_image
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
    }

    for attempt in range(1, Config.API_RETRY_ATTEMPTS + 1):
        response = None
        try:
            response = requests_session.post(
                Config.CLAUDE_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=Config.API_TIMEOUT
            )

            if response.status_code == 200:
                try:
                    result = response.json()

                    if "content" not in result:
                        logger.error("API response missing 'content' field")
                        return False, "Error: Invalid API response (no content)"

                    if not result["content"] or len(result["content"]) == 0:
                        logger.error("API response has empty content array")
                        return False, "Error: Empty API response"

                    if "text" not in result["content"][0]:
                        logger.error("API response missing 'text' field")
                        return False, "Error: Invalid API response (no text)"

                    response_text = result["content"][0]["text"]

                    if not response_text:
                        logger.error("API returned empty text")
                        return False, "Error: Empty response from Claude"

                    print("="*60)
                    print(f"PROMPT: {prompt_label}")
                    print("="*60)
                    print(response_text)
                    print("="*60)
                    print("")

                    try:
                        save_response(image_path, response_text, prompt_label)
                    except Exception as e:
                        logger.warn("Save failed: {}", e)

                    del base64_image, result
                    gc.collect()

                    return True, response_text

                except KeyError as e:
                    logger.error("Missing key in API response: {}", e)
                    return False, f"Error: Bad API response structure"
                except IndexError as e:
                    logger.error("Index error parsing API response: {}", e)
                    return False, f"Error: Invalid API response format"

            elif response.status_code == 429:
                logger.warn("Rate limited - retry {}/{}", attempt, Config.API_RETRY_ATTEMPTS)
                if attempt < Config.API_RETRY_ATTEMPTS:
                    time.sleep(Config.API_RETRY_DELAY * 2)
                    continue
                return False, "Error: Rate limited"

            elif response.status_code == 401:
                return False, "Error: Invalid API key"

            elif response.status_code == 400:
                try:
                    error_msg = response.json().get("error", {}).get("message", "Bad request")
                except (ValueError, KeyError, AttributeError):
                    error_msg = "Bad request"
                logger.error("API error: {}", error_msg)
                return False, f"Error: {error_msg[:30]}"

            else:
                logger.warn("HTTP {}", response.status_code)
                if attempt < Config.API_RETRY_ATTEMPTS:
                    time.sleep(Config.API_RETRY_DELAY)
                    continue
                return False, f"Error: HTTP {response.status_code}"

        except OSError as e:
            error_str = str(e)
            if "timed out" in error_str.lower() or "timeout" in error_str.lower():
                logger.error("API timeout on attempt {}/{}", attempt, Config.API_RETRY_ATTEMPTS)
                if attempt < Config.API_RETRY_ATTEMPTS:
                    logger.info("Retrying... (attempt {} of {})", attempt + 1, Config.API_RETRY_ATTEMPTS)
                    time.sleep(Config.API_RETRY_DELAY)
                    continue
                return False, "Error: API timeout"
            else:
                logger.error("Network error: {}", error_str[:50])
                if attempt < Config.API_RETRY_ATTEMPTS:
                    time.sleep(Config.API_RETRY_DELAY)
                    continue
                return False, f"Error: Network {error_str[:20]}"

        except Exception as e:
            logger.error("Request failed: {}", str(e)[:50])
            if attempt < Config.API_RETRY_ATTEMPTS:
                time.sleep(Config.API_RETRY_DELAY)
                continue
            return False, f"Error: {str(e)[:30]}"

        finally:
            if response:
                response.close()
            gc.collect()

    return False, "Error: All retries failed"

def save_response(image_path, response_text, prompt_label):
    """Save Claude response as text file"""
    try:
        if not image_path or not response_text:
            logger.warn("Cannot save: missing image_path or response_text")
            return False

        txt_filename = image_path.replace('.jpg', '.txt')
        txt_filename = txt_filename[:11] + f"_{prompt_label}" + txt_filename[11:]

        if "?" in txt_filename:
            txt_filename = txt_filename.replace("?", "")

        with open(txt_filename, "w") as fp:
            fp.write(response_text)
            fp.flush()

        filename_only = txt_filename.split('/')[-1]
        logger.info("Saved response to: {}", filename_only)
        return True

    except (OSError, ValueError) as e:
        logger.error("Failed to save response: {}", e)
        return False

# ============================================================================
# SCROLLABLE TEXT VIEWER
# ============================================================================

class TextViewer:
    """Scrollable text viewer"""

    def __init__(self, pycam):
        self.pycam = pycam
        self.full_text = ""
        self.lines = []
        self.scroll_pos = 0
        self.lines_per_page = Config.LINES_PER_PAGE
        self.palette = displayio.Palette(1)
        self.palette[0] = 0x000000
        self.rectangle = None
        self.text_area = None
        self.page_indicator = None
        self.is_active = False
        self.current_prompt_label = ""

    def show(self, text, prompt_label):
        """Display text with scrolling support"""
        try:
            self.full_text = text
            self.scroll_pos = 0
            self.current_prompt_label = prompt_label
            self.is_active = True

            wrapped_text = "\n".join(wrap_text_to_lines(text, Config.TEXT_WRAP_WIDTH))

            if "haiku" in prompt_label.lower():
                wrapped_text = wrapped_text.replace("*", "\n")

            self.lines = wrapped_text.split('\n')

            self.rectangle = vectorio.Rectangle(
                pixel_shader=self.palette,
                width=240,
                height=240,
                x=0,
                y=0
            )
            self.pycam.splash.append(self.rectangle)

            self._render_page()

            logger.info("Text viewer active - {} lines total", len(self.lines))

        except Exception as e:
            logger.error("Failed to display text: {}", e)
            self.is_active = False

    def _render_page(self):
        """Render the current page of text"""
        try:
            if self.text_area:
                try:
                    self.pycam.splash.remove(self.text_area)
                except (ValueError, AttributeError):
                    pass
            if self.page_indicator:
                try:
                    self.pycam.splash.remove(self.page_indicator)
                except (ValueError, AttributeError):
                    pass

            start_line = self.scroll_pos
            end_line = min(start_line + self.lines_per_page, len(self.lines))
            visible_text = '\n'.join(self.lines[start_line:end_line])

            self.text_area = label.Label(
                terminalio.FONT,
                text=visible_text,
                color=0xFFFFFF,
                x=2,
                y=Config.TEXT_Y_POSITION,
                scale=Config.TEXT_SCALE
            )
            self.pycam.splash.append(self.text_area)

            total_pages = max(1, (len(self.lines) + self.lines_per_page - 1) // self.lines_per_page)
            current_page = min(total_pages, (self.scroll_pos // self.lines_per_page) + 1)

            if total_pages > 1:
                can_go_up = self.scroll_pos > 0
                can_go_down = (self.scroll_pos + self.lines_per_page) < len(self.lines)

                if can_go_up and can_go_down:
                    indicator_text = "Go Up or Down"
                elif can_go_up:
                    indicator_text = "Go Up"
                elif can_go_down:
                    indicator_text = "Go Down"
                else:
                    indicator_text = f"Page {current_page}/{total_pages}"

                self.page_indicator = label.Label(
                    terminalio.FONT,
                    text=indicator_text,
                    color=0x00FFFF,
                    x=5,
                    y=232,
                    scale=1
                )
                self.pycam.splash.append(self.page_indicator)
            else:
                self.page_indicator = label.Label(
                    terminalio.FONT,
                    text="OK to close",
                    color=0x00FF00,
                    x=5,
                    y=232,
                    scale=1
                )
                self.pycam.splash.append(self.page_indicator)

            self.pycam.display.refresh()

        except Exception as e:
            logger.error("Failed to render page: {}", e)

    def scroll_up(self):
        """Scroll up (show previous lines)"""
        if not self.is_active:
            return False

        if self.scroll_pos > 0:
            self.scroll_pos = max(0, self.scroll_pos - 3)
            self._render_page()
            logger.info("Scrolled up to line {}", self.scroll_pos)
            return True
        else:
            logger.info("Already at top")
        return False

    def scroll_down(self):
        """Scroll down (show next lines)"""
        if not self.is_active:
            return False

        max_scroll = max(0, len(self.lines) - self.lines_per_page)
        if self.scroll_pos < max_scroll:
            self.scroll_pos = min(max_scroll, self.scroll_pos + 3)
            self._render_page()
            logger.info("Scrolled down to line {}", self.scroll_pos)
            return True
        else:
            logger.info("Already at bottom")
        return False

    def clear(self):
        """Clear the text viewer"""
        if self.rectangle:
            try:
                self.pycam.splash.remove(self.rectangle)
            except (ValueError, AttributeError):
                pass
        if self.text_area:
            try:
                self.pycam.splash.remove(self.text_area)
            except (ValueError, AttributeError):
                pass
        if self.page_indicator:
            try:
                self.pycam.splash.remove(self.page_indicator)
            except (ValueError, AttributeError):
                pass

        self.rectangle = None
        self.text_area = None
        self.page_indicator = None
        self.is_active = False
        logger.info("Text viewer closed")

# ============================================================================
# DISPLAY UTILITIES
# ============================================================================

def show_status_overlay(pycam, status_text, color=0xFFFFFF):
    """Show small status text overlaid on current display"""
    try:
        pycam._botbar.hidden = True

        for item in pycam.splash:
            if hasattr(item, '_status_overlay'):
                try:
                    pycam.splash.remove(item)
                except (ValueError, AttributeError):
                    pass

        status_label = label.Label(
            terminalio.FONT,
            text=status_text,
            color=color,
            background_color=0x000000,
            x=5,
            y=225,
            scale=1
        )
        status_label._status_overlay = True
        pycam.splash.append(status_label)
        pycam.display.refresh()

    except Exception as e:
        logger.warn("Could not show status overlay: {}", e)

def clear_status_overlay(pycam):
    """Clear any status overlay text"""
    try:
        pycam._botbar.hidden = False

        for item in pycam.splash:
            if hasattr(item, '_status_overlay'):
                try:
                    pycam.splash.remove(item)
                except (ValueError, AttributeError):
                    pass
        pycam.display.refresh()
    except (AttributeError, RuntimeError):
        pass

def load_image_on_screen(pycam, bitmap, decoder, filepath):
    """Load and display image from SD card"""
    try:
        bitmap.fill(0b00000_000000_00000)
        decoder.open(filepath)
        decoder.decode(bitmap, scale=0, x=0, y=0)
        pycam.blit(bitmap)
        pycam.display.refresh()

        filename_only = filepath.split('/')[-1]
        logger.info("Displayed: {}", filename_only)

    except Exception as e:
        logger.error("Failed to load image {}: {}", filepath.split('/')[-1], e)

def get_sorted_images():
    """Get sorted list of images from SD card"""
    try:
        all_images = [
            f"/sd/{filename}"
            for filename in os.listdir("/sd")
            if filename.lower().endswith(".jpg")
        ]

        def safe_extract_number(filename):
            digits = ''.join(filter(str.isdigit, filename))
            try:
                return int(digits) if digits and len(digits) < 10 else 0
            except (ValueError, OverflowError):
                return 0

        all_images.sort(key=safe_extract_number)
        return all_images
    except Exception as e:
        logger.error("Failed to list images: {}", e)
        return []

def get_newest_image():
    """Get the most recent image from SD card - FAST version for post-capture"""
    try:
        newest = None
        newest_time = 0

        for filename in os.listdir("/sd"):
            if filename.lower().endswith(".jpg"):
                filepath = f"/sd/{filename}"
                try:
                    stat = os.stat(filepath)
                    mtime = stat[8]  # Modification time
                    if mtime > newest_time:
                        newest_time = mtime
                        newest = filepath
                except (OSError, IndexError):
                    pass

        return newest
    except (OSError, RuntimeError) as e:
        logger.error("Failed to get newest image: {}", e)
        return None

def check_sd_card():
    """Check if SD card is mounted and accessible"""
    try:
        os.listdir("/sd")
        return True
    except (OSError, RuntimeError):
        return False

def change_quality_mode(pycam, quality_mode_index, quality_txt):
    """Change quality mode and update display - consolidated function"""
    current_mode = Config.QUALITY_MODE_ORDER[quality_mode_index]
    mode_info = Config.get_quality_mode_info(current_mode)

    pycam.resolution = mode_info["resolution"]
    quality_txt.text = f"{mode_info['icon']} {mode_info['label']}"
    pycam.display.refresh()

    logger.info("Quality: {} {} (~{}KB, max ~{}KB)",
                mode_info['icon'], mode_info['label'],
                mode_info['target_kb'], mode_info.get('max_expected_kb', 'unknown'))

    return mode_info

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""

    print("="*50)
    print("CloudLens - AI Vision Camera")
    print("CircuitPython 10.x - Version 1.0 Beta")
    print("="*50)

    # Validate configuration
    issues = Config.validate()
    if issues:
        logger.warn("Configuration issues found:")
        for issue in issues:
            logger.warn("  - {}", issue)
        if not Config.ANTHROPIC_API_KEY:
            logger.error("Cannot continue without API key")
            return

    Config.validate_camera_resolution()

    # Check SD card availability
    if not check_sd_card():
        logger.error("SD card not found or not mounted")
        logger.error("Please insert SD card and restart")
        return

    logger.info("SD card detected")

    # Connect to WiFi
    requests = connect_wifi()
    if not requests:
        logger.error("Cannot continue without WiFi")
        return

    # Initialize camera
    logger.info("Initializing camera...")
    try:
        pycam = adafruit_pycamera.PyCamera()
        pycam.mode = 0

        quality_mode = Config.validate_quality_mode(Config.DEFAULT_QUALITY_MODE)
        mode_info = Config.get_quality_mode_info(quality_mode)
        pycam.resolution = mode_info["resolution"]

        pycam.effect = 0

        # Hide PyCamera's built-in status displays (resolution, SD status, etc.)
        try:
            if hasattr(pycam, '_topbar'):
                pycam._topbar.hidden = True
                logger.info("PyCamera built-in status bar hidden")
        except (AttributeError, RuntimeError):
            pass

        logger.info("Camera ready")
        logger.info("Quality mode: {} (resolution {})", quality_mode, mode_info["resolution"])
    except Exception as e:
        logger.error("Camera initialization failed: {}", e)
        return

    # Initialize display components
    palette = displayio.Palette(1)
    palette[0] = 0x000000
    decoder = JpegDecoder()
    browse_bitmap = displayio.Bitmap(240, 240, 65535)

    # Initialize text viewer
    text_viewer = TextViewer(pycam)

    # Load prompts dynamically from config
    prompts, prompt_labels = Config.get_prompts()
    num_prompts = len(prompts)

    if num_prompts == 0:
        logger.error("No prompts loaded! Check settings.toml")
        return

    logger.info("Loaded {} prompts: {}", num_prompts, ", ".join(prompt_labels))

    prompt_index = 0
    quality_mode_index = Config.QUALITY_MODE_ORDER.index(quality_mode)

    # Add prompt label to bottom bar
    rect = vectorio.Rectangle(
        pixel_shader=palette,
        width=240,
        height=20,
        x=0,
        y=0
    )
    prompt_txt = label.Label(
        terminalio.FONT,
        text=prompt_labels[prompt_index],
        color=0x00DDFF,
        x=10,
        y=15,
        scale=2
    )

    # Add quality mode indicator to lower-right corner
    quality_txt = label.Label(
        terminalio.FONT,
        text=f"{mode_info['icon']} {mode_info['label']}",
        color=0x00DDFF,
        x=140,
        y=220,
        scale=1
    )

    # Add CloudLens branding to top-left
    branding_txt = label.Label(
        terminalio.FONT,
        text="CloudLens",
        color=0x00FF00,
        x=5,
        y=8,
        scale=1
    )

    pycam._botbar.append(rect)
    pycam._botbar.append(prompt_txt)
    pycam.splash.append(quality_txt)
    pycam.splash.append(branding_txt)
    pycam.display.refresh()

    # Application state
    system_ready = False
    ready_message_cleared = False  # Track when READY message is fully cleared
    showing_captured_image = False
    view_mode = False
    browse_mode = False
    file_index = -1
    all_images = get_sorted_images()

    # Show READY message to user
    pycam.display_message("READY!", color=0x00FF00)
    time.sleep(1.5)

    # Clear READY message and start viewfinder
    pycam.display.refresh()
    time.sleep(0.3)  # Brief delay to ensure message is cleared
    system_ready = True

    logger.info("Ready! Controls:")
    logger.info("  LEFT/RIGHT: Change prompt mode")
    logger.info("  UP/DOWN: Change quality mode (or scroll text)")
    logger.info("  SELECT: Browse saved images")
    logger.info("  OK: Close text or send browsed image")
    logger.info("  SHUTTER: Take photo & analyze")

    # MAIN LOOP
    while True:
        try:
            if not system_ready:
                pycam.display_message("Starting...", color=0xFFFF00)
            elif browse_mode:
                pass
            elif showing_captured_image:
                pass
            elif not view_mode:
                try:
                    frame = pycam.continuous_capture()
                    if frame and hasattr(frame, 'width') and hasattr(frame, 'height'):
                        pycam.blit(frame)
                        # Mark READY message as cleared after first frame
                        if not ready_message_cleared:
                            ready_message_cleared = True
                except (RuntimeError, AttributeError, OSError):
                    pass

            pycam.keys_debounce()

            if not system_ready or not ready_message_cleared:
                continue

            # SHUTTER BUTTON - Now blocked until READY message is cleared and viewfinder running
            if pycam.shutter.long_press and not view_mode:
                logger.info("Autofocus triggered")
                pycam.autofocus()

            if pycam.shutter.short_count and not view_mode:
                logger.info("Capture triggered")

                try:
                    current_mode = Config.QUALITY_MODE_ORDER[quality_mode_index]
                    mode_info = Config.get_quality_mode_info(current_mode)
                    logger.info("Capturing with {} mode (resolution {})", current_mode, mode_info["resolution"])

                    flash_enabled = False
                    if Config.AUTO_FLASH_ENABLED:
                        is_dark = check_brightness(pycam)
                        if is_dark:
                            pycam.led_level = 4
                            pycam.led_color = 0
                            flash_enabled = True
                            logger.info("Flash enabled for dark scene")
                            time.sleep(0.1)

                    pycam.capture_jpeg()

                    # IMMEDIATE feedback that photo was taken
                    pycam.display_message("SNAP!", color=0x00FF00)
                    time.sleep(0.3)  # Brief confirmation

                    if flash_enabled:
                        pycam.led_level = 0
                        logger.info("Flash disabled")

                    # FAST: Get newest image by modification time (no sorting)
                    the_image = get_newest_image()
                    if not the_image:
                        pycam.display_message("No images", color=0xFF0000)
                        time.sleep(Config.MSG_DURATION)
                        gc.collect()
                        continue

                    filename_only = the_image.split('/')[-1]
                    logger.info("Captured: {}", filename_only)

                    is_ok, size_kb, size_msg = check_image_size(the_image, mode_info)
                    logger.info("Image size: {}", size_msg)

                    if not is_ok:
                        pycam.display_message(f"TOO LARGE!\n{size_kb}KB > 3MB\nTry lower mode", color=0xFF0000)
                        time.sleep(3)
                        gc.collect()
                        continue

                    showing_captured_image = True

                    # Immediate send - no delay
                    show_status_overlay(pycam, "Sending to Claude...", 0x00DDDD)

                    success, response = send_to_claude(
                        requests,
                        the_image,
                        prompts[prompt_index],
                        prompt_labels[prompt_index]
                    )

                    showing_captured_image = False

                    if success:
                        clear_status_overlay(pycam)
                        text_viewer.show(response, prompt_labels[prompt_index])
                        view_mode = True
                        del response  # Free memory
                        gc.collect()
                    else:
                        clear_status_overlay(pycam)
                        pycam.display_message(response, color=0xFF0000)
                        time.sleep(2)
                        gc.collect()

                except TypeError as e:
                    logger.error("Capture failed (TypeError): {}", e)
                    pycam.display_message("Failed", color=0xFF0000)
                    time.sleep(Config.MSG_DURATION)
                    pycam.live_preview_mode()
                    gc.collect()

                except RuntimeError as e:
                    logger.error("No SD card: {}", e)
                    pycam.display_message("Error\nNo SD Card", color=0xFF0000)
                    time.sleep(Config.MSG_DURATION)
                    gc.collect()

                except Exception as e:
                    logger.error("Unexpected error: {}", e)
                    pycam.display_message("Error", color=0xFF0000)
                    time.sleep(Config.MSG_DURATION)
                    gc.collect()

            # UP/DOWN - Scroll text OR change quality mode
            if pycam.up.fell:
                if view_mode:
                    text_viewer.scroll_up()
                elif not browse_mode:
                    quality_mode_index = (quality_mode_index + 1) % len(Config.QUALITY_MODE_ORDER)
                    mode_info = change_quality_mode(pycam, quality_mode_index, quality_txt)

            if pycam.down.fell:
                if view_mode:
                    text_viewer.scroll_down()
                elif not browse_mode:
                    quality_mode_index = (quality_mode_index - 1) % len(Config.QUALITY_MODE_ORDER)
                    mode_info = change_quality_mode(pycam, quality_mode_index, quality_txt)

            # LEFT/RIGHT - Navigate
            if pycam.right.fell:
                if browse_mode:
                    file_index = (file_index + 1) % len(all_images)
                    filename = all_images[file_index]
                    load_image_on_screen(pycam, browse_bitmap, decoder, filename)
                elif not view_mode:
                    prompt_index = (prompt_index + 1) % num_prompts
                    prompt_txt.text = prompt_labels[prompt_index]
                    pycam.display.refresh()
                    logger.info("Prompt: {}", prompt_labels[prompt_index])

            if pycam.left.fell:
                if browse_mode:
                    file_index = (file_index - 1) % len(all_images)
                    filename = all_images[file_index]
                    load_image_on_screen(pycam, browse_bitmap, decoder, filename)
                elif not view_mode:
                    prompt_index = (prompt_index - 1) % num_prompts
                    prompt_txt.text = prompt_labels[prompt_index]
                    pycam.display.refresh()
                    logger.info("Prompt: {}", prompt_labels[prompt_index])

            # SELECT - Browse mode
            if pycam.select.fell:
                if not browse_mode and not view_mode:
                    all_images = get_sorted_images()
                    if all_images:
                        file_index = -1
                        browse_mode = True
                        filename = all_images[file_index]
                        load_image_on_screen(pycam, browse_bitmap, decoder, filename)
                        logger.info("Browse mode: ON (LEFT/RIGHT to navigate, OK to send)")
                    else:
                        pycam.display_message("No images", color=0xFF0000)
                        time.sleep(Config.MSG_DURATION)
                elif browse_mode:
                    browse_mode = False
                    pycam.display.refresh()
                    logger.info("Browse mode: OFF")

            # OK - Confirm/Close
            if pycam.ok.fell:
                if view_mode:
                    text_viewer.clear()
                    showing_captured_image = False
                    view_mode = False
                    try:
                        pycam.live_preview_mode()
                    except (RuntimeError, AttributeError):
                        pass
                    pycam.display.refresh()
                    logger.info("Closed text view, restarting viewfinder")

                elif browse_mode:
                    filename = all_images[file_index]
                    filename_only = filename.split('/')[-1]
                    logger.info("Sending browsed image: {}", filename_only)

                    show_status_overlay(pycam, "Sending to Claude...", 0x00DDDD)

                    success, response = send_to_claude(
                        requests,
                        filename,
                        prompts[prompt_index],
                        prompt_labels[prompt_index]
                    )

                    if success:
                        browse_mode = False
                        clear_status_overlay(pycam)
                        text_viewer.show(response, prompt_labels[prompt_index])
                        view_mode = True
                        del response  # Free memory
                        gc.collect()
                    else:
                        clear_status_overlay(pycam)
                        pycam.display_message(response, color=0xFF0000)
                        time.sleep(2)
                        pycam.display.refresh()
                        gc.collect()

            gc.collect()

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break

        except Exception as e:
            logger.error("Main loop error: {}", e)
            try:
                pycam.display_message("System Error", color=0xFF0000)
                time.sleep(1)
                pycam.display.refresh()
            except (RuntimeError, AttributeError):
                pass
            gc.collect()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Fatal error: {}", e)
        print("System halted. Please reset device.")
