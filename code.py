"""
CloudLens - AI Vision for CircuitPython
An educational IoT project demonstrating camera integration with Anthropic Claude API.

Author: William Chesher
License: MIT
"""

import time
import board
import wifi
import socketpool
import ssl
import adafruit_requests
import os

# ============================================
# CONFIGURATION LOADING
# ============================================

def load_config():
    """Load settings from settings.toml and secrets from secrets.toml"""
    try:
        import toml
    except ImportError:
        print("✗ TOML library not available - using os.getenv for secrets")
        toml = None

    config = {}

    # Load secrets from environment (CircuitPython reads secrets.toml into env)
    config['wifi_ssid'] = os.getenv('CIRCUITPY_WIFI_SSID')
    config['wifi_password'] = os.getenv('CIRCUITPY_WIFI_PASSWORD')
    config['api_key'] = os.getenv('ANTHROPIC_API_KEY')

    # Load settings from settings.toml if available
    if toml:
        try:
            with open('/settings.toml', 'r') as f:
                settings = toml.load(f)
                config.update({
                    'camera_resolution': settings.get('camera', {}).get('resolution', 1),
                    'auto_flash': settings.get('flash', {}).get('auto_flash_enabled', True),
                    'flash_threshold': settings.get('flash', {}).get('dark_threshold', 30),
                    'api_model': settings.get('api', {}).get('model', 'claude-3-5-sonnet-20241022'),
                    'max_tokens': settings.get('api', {}).get('max_tokens', 1024),
                    'api_timeout': settings.get('api', {}).get('timeout', 30),
                    'max_retries': settings.get('network', {}).get('max_retries', 3),
                    'retry_delay': settings.get('network', {}).get('retry_delay', 2),
                    'prompts': settings.get('prompts', {})
                })
        except Exception as e:
            print(f"⚠ Could not load settings.toml: {e}")
            # Use defaults
            config.update({
                'camera_resolution': 1,
                'auto_flash': True,
                'flash_threshold': 30,
                'api_model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 1024,
                'api_timeout': 30,
                'max_retries': 3,
                'retry_delay': 2,
                'prompts': {}
            })

    return config


# ============================================
# NETWORK FUNCTIONS
# ============================================

def connect_wifi(ssid, password, max_retries=3, retry_delay=2):
    """Connect to WiFi with retry logic"""
    print(f"Connecting to WiFi: {ssid}")

    for attempt in range(max_retries):
        try:
            wifi.radio.connect(ssid, password, timeout=10)
            print(f"✓ Connected to WiFi")
            print(f"  IP Address: {wifi.radio.ipv4_address}")
            return True
        except Exception as e:
            print(f"✗ WiFi attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

    return False


def create_requests_session():
    """Create HTTPS requests session"""
    pool = socketpool.SocketPool(wifi.radio)
    ssl_context = ssl.create_default_context()
    return adafruit_requests.Session(pool, ssl_context)


# ============================================
# CAMERA FUNCTIONS
# ============================================

def init_camera(resolution=1):
    """
    Initialize camera hardware.
    Adjust this based on your specific camera module.

    Common resolutions:
    0 = 240x240
    1 = 320x240
    2 = 640x480
    """
    print(f"Initializing camera (resolution: {resolution})...")

    try:
        # TODO: Uncomment and adjust for your camera module
        # Example for ESP32-S3 with camera:
        # import espcamera
        # camera = espcamera.Camera(
        #     data_pins=board.CAMERA_DATA,
        #     external_clock_pin=board.CAMERA_XCLK,
        #     pixel_clock_pin=board.CAMERA_PCLK,
        #     vsync_pin=board.CAMERA_VSYNC,
        #     href_pin=board.CAMERA_HREF,
        #     pixel_format=espcamera.PixelFormat.JPEG,
        #     frame_size=resolution,
        #     jpeg_quality=10,
        # )
        # print("✓ Camera initialized")
        # return camera

        print("⚠ Camera initialization not implemented - using placeholder")
        return None

    except Exception as e:
        print(f"✗ Camera initialization failed: {e}")
        return None


def capture_image(camera):
    """Capture image from camera"""
    if camera is None:
        print("⚠ No camera available - using placeholder")
        return None

    try:
        print("Capturing image...")
        # TODO: Adjust for your camera API
        # frame = camera.take()
        # print("✓ Image captured")
        # return frame

        return None
    except Exception as e:
        print(f"✗ Image capture failed: {e}")
        return None


# ============================================
# AI VISION FUNCTIONS
# ============================================

def analyze_image(requests, image_data, prompt, api_key, model='claude-3-5-sonnet-20241022', max_tokens=1024):
    """
    Send image to Claude API for analysis

    Args:
        requests: adafruit_requests session
        image_data: JPEG image bytes
        prompt: Text prompt for analysis
        api_key: Anthropic API key
        model: Claude model to use
        max_tokens: Maximum response tokens

    Returns:
        str: Claude's response text
    """
    print(f"Sending to Claude API...")

    if image_data is None:
        print("⚠ No image data - skipping API call")
        return "No image data available for analysis"

    try:
        # Encode image as base64
        import binascii
        image_b64 = binascii.b2a_base64(image_data).decode('ascii').strip()

        url = "https://api.anthropic.com/v1/messages"

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response_data = response.json()
        text = response_data["content"][0]["text"]

        print(f"✓ Response received ({len(text)} characters)")
        return text

    except Exception as e:
        print(f"✗ API request failed: {e}")
        return f"Error: {e}"


# ============================================
# MAIN PROGRAM
# ============================================

def main():
    """Main program loop"""

    print("\n" + "=" * 40)
    print("CloudLens - AI Vision for CircuitPython")
    print("=" * 40 + "\n")

    # Load configuration
    print("Loading configuration...")
    config = load_config()

    if not config.get('wifi_ssid') or not config.get('api_key'):
        print("✗ Missing WiFi or API credentials in secrets.toml")
        print("Please configure secrets.toml and reset device")
        while True:
            time.sleep(60)

    print("✓ Configuration loaded")

    # Connect to WiFi
    if not connect_wifi(
        config['wifi_ssid'],
        config['wifi_password'],
        config.get('max_retries', 3),
        config.get('retry_delay', 2)
    ):
        print("✗ Cannot proceed without WiFi")
        while True:
            time.sleep(60)

    # Initialize requests
    print("Initializing HTTPS...")
    requests = create_requests_session()
    print("✓ HTTPS ready")

    # Initialize camera
    camera = init_camera(config.get('camera_resolution', 1))

    # Default prompt if no settings.toml
    default_prompt = "Describe this image in detail, focusing on what would be most useful for accessibility."

    print("\n✓ Initialization complete")
    print("Ready for image capture!\n")

    # Main loop
    while True:
        try:
            print("=" * 40)
            print("Press button to capture (or waiting 10 seconds...)")

            # TODO: Replace with actual button detection
            time.sleep(10)

            # Capture image
            image_data = capture_image(camera)

            # Analyze with Claude
            response = analyze_image(
                requests,
                image_data,
                default_prompt,
                config['api_key'],
                config.get('api_model', 'claude-3-5-sonnet-20241022'),
                config.get('max_tokens', 1024)
            )

            # Display response
            print("\n" + "=" * 40)
            print("CLAUDE RESPONSE:")
            print("=" * 40)
            print(response)
            print("=" * 40 + "\n")

        except KeyboardInterrupt:
            print("\n\nShutting down...")
            break
        except Exception as e:
            print(f"\n✗ Error in main loop: {e}")
            print("Continuing after 5 seconds...")
            time.sleep(5)


# Entry point
if __name__ == "__main__":
    main()
