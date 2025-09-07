#!/usr/bin/env python3
"""
MUNI L-Taraval Real-time Arrival Display
Shows live arrival times for L-Taraval line on 64x32 RGB matrix.
"""

import sys
import os
import time
import requests
import json
from datetime import datetime, timedelta
import threading
import configparser

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from matrix.emulator_controller import EmulatorController


class MuniLTaravalDisplay:
    """Real-time MUNI L-Taraval arrival display."""

    def __init__(self, api_key=None, config_file="examples/muni.config"):
        """Initialize the MUNI display."""
        self.api_key = api_key or "YOUR_511_API_KEY_HERE"
        self.controller = EmulatorController(use_emulator=True)
        self.running = False
        self.arrivals_data = []
        self.last_update = None

        # Load configuration from file
        self.config = self._load_config(config_file)

        # MUNI line configuration
        self.agency = "SF"  # San Francisco MUNI

        # Load line from config file, fallback to default
        config_line = self.config.get('LINE', 'L-Taraval')
        self.line_name = config_line
        # Extract line ID (first character before space or dash)
        if ' ' in config_line:
            self.line_id = config_line.split(' ')[0]
        elif '-' in config_line:
            self.line_id = config_line.split('-')[0]
        else:
            self.line_id = config_line[0] if config_line else "L"

        # MUNI Line Color Table (RGB values)
        self.muni_line_colors = {
            "L": (128, 0, 128),     # L-Taraval - Purple
            "N": (0, 100, 200),     # N-Judah - Blue
            "M": (0, 150, 0),       # M-Ocean View - Green
            "K": (255, 165, 0),     # K-Ingleside - Orange
            "J": (255, 255, 0),     # J-Church - Yellow
            "T": (255, 0, 0),       # T-Third Street - Red
            "S": (255, 192, 203),   # S-Castro Shuttle - Pink
            "F": (139, 69, 19),     # F-Market & Wharves - Brown
            "E": (128, 128, 128),   # E-Embarcadero - Gray
            "1": (0, 255, 255),     # 1-California - Cyan
            "2": (255, 20, 147),    # 2-Clement - Deep Pink
            "3": (50, 205, 50),     # 3-Jackson - Lime Green
            "5": (255, 140, 0),     # 5-Fulton - Dark Orange
            "6": (75, 0, 130),      # 6-Haight-Parnassus - Indigo
            "7": (220, 20, 60),     # 7-Haight-Noriega - Crimson
            "8": (0, 191, 255),     # 8-Bayshore - Deep Sky Blue
            "9": (255, 105, 180),   # 9-San Bruno - Hot Pink
            "10": (34, 139, 34),    # 10-Townsend - Forest Green
            "12": (255, 69, 0),     # 12-Folsom-Pacific - Red Orange
            "14": (138, 43, 226),   # 14-Mission - Blue Violet
            "15": (255, 215, 0),    # 15-Kearny - Gold
            "19": (72, 61, 139),    # 19-Polk - Dark Slate Blue
            "22": (255, 99, 71),    # 22-Fillmore - Tomato
            "24": (147, 112, 219),  # 24-Divisadero - Medium Purple
            "28": (0, 206, 209),    # 28-19th Avenue - Dark Turquoise
            "29": (255, 182, 193),  # 29-Sunset - Light Pink
            "30": (106, 90, 205),   # 30-Stockton - Slate Blue
            "31": (255, 160, 122),  # 31-Balboa - Light Salmon
            "33": (64, 224, 208),   # 33-Ashbury-18th St - Turquoise
            "38": (255, 127, 80),   # 38-Geary - Coral
            "43": (123, 104, 238),  # 43-Masonic - Medium Slate Blue
            "44": (240, 230, 140),  # 44-O'Shaughnessy - Khaki
            "45": (221, 160, 221),  # 45-Union-Stockton - Plum
            "47": (176, 196, 222),  # 47-Van Ness - Light Steel Blue
            "49": (205, 92, 92),    # 49-Mission-Van Ness - Indian Red
        }

        # Get the color for the current line
        self.line_color = self.muni_line_colors.get(self.line_id, (255, 255, 255))  # Default to white

        # Popular L-Taraval stops (real MUNI stop IDs)
        self.stops = {
            "Embarcadero": "13218",     # Embarcadero Station
            "Montgomery": "13217",      # Montgomery Station
            "Powell": "13216",          # Powell Station
            "Civic Center": "13215",    # Civic Center Station
            "Van Ness": "13214",        # Van Ness Station
            "Church": "13213",          # Church Station
            "Castro": "13212",          # Castro Station
            "Forest Hill": "13211",     # Forest Hill Station
            "West Portal": "13210",     # West Portal Station
            "Sunset Blvd": "13209",     # Sunset Boulevard
            "19th Ave": "13208",        # 19th Avenue
            "Taraval/17th": "16615",    # Taraval & 17th Ave
            "Taraval/17th Ave": "16615", # Alternative name from config
            "Taraval/46th": "13207",    # Taraval & 46th Ave
            "SF Zoo": "13206"           # SF Zoo (end of line)
        }

        # Load stop from config file, fallback to default
        config_stop_name = self.config.get('STOP_NAME', 'Taraval/17th')
        self.current_stop = config_stop_name if config_stop_name in self.stops else "Taraval/17th"
        self.current_stop_id = self.stops[self.current_stop]

        # Load direction from config file, fallback to default
        config_direction = self.config.get('DIRECTION', 'Inbound')
        self.direction = config_direction
        self.direction_id = 1 if config_direction.lower() == 'inbound' else 0
        self.direction_display = "I" if config_direction.lower() == 'inbound' else "O"

        # Animation state for train towing updates
        self.animation_active = False
        self.animation_frame = 0
        self.animation_total_frames = 120  # Total frames for animation (6 seconds at 20fps)
        self.animation_phase = "entering"  # "exiting" or "entering"
        self.current_arrivals = []  # Track current arrivals to detect changes
        self.start_time = time.time()  # Track startup time for test trigger
        self.old_arrival_text = ""  # Store old arrival text for exit animation

        # Test mode configuration
        self.test_mode = self.config.get('TEST_MODE', 'false').lower() == 'true'
        self.test_data = []
        self.test_data_index = 0
        if self.test_mode:
            self.load_test_data()

        # Update interval configuration
        if self.test_mode:
            self.update_interval = int(self.config.get('TEST_UPDATE_INTERVAL', 8))
        else:
            self.update_interval = int(self.config.get('UPDATE_INTERVAL', 30))

        # Debug mode configuration
        self.debug_mode = self.config.get('DEBUG_MODE', 'false').lower() == 'true'

        # Track next update time
        self.next_update_time = None
        self.last_data_fetch_time = 0  # Track when we last fetched new data

        # Persistent display state - what to show until next data update
        self.display_arrival_text = "NO DATA"
        self.display_arrival_color = (255, 255, 0)  # Default yellow

        # Store old arrival info for exit animation
        self.old_arrival_color = (255, 255, 0)  # Default yellow

    def _load_config(self, config_file):
        """Load configuration from muni.config file."""
        config = {}
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Remove quotes from value if present
                            value = value.strip().strip('"').strip("'")
                            config[key.strip()] = value
                print(f"✅ Loaded configuration from {config_file}")
                print(f"   STOP_NAME: {config.get('STOP_NAME', 'Not set')}")
            else:
                print(f"⚠️  Config file {config_file} not found, using defaults")
        except Exception as e:
            print(f"⚠️  Error loading config file {config_file}: {e}")
        return config

    def get_line_color(self, line_id):
        """Get the official MUNI color for a given line."""
        return self.muni_line_colors.get(line_id.upper(), (255, 255, 255))

    def get_api_key_instructions(self):
        """Show instructions for getting a 511.org API key."""
        print("🔑 To get real MUNI data, you need a free 511.org API key:")
        print("   1. Go to: https://511.org/open-data/token")
        print("   2. Fill out the form (it's free!)")
        print("   3. You'll receive your API key via email")
        print("   4. Set environment variable: export MUNI_API_KEY=your_key")
        print()
    
    def get_demo_data(self):
        """Generate demo arrival data for testing."""
        now = datetime.now()

        # Generate direction-specific destinations
        if self.direction.lower() == 'inbound':
            # Inbound trains go toward downtown
            destinations = ['Embarcadero', 'Montgomery', 'Powell', 'Civic Center']
        else:
            # Outbound trains go toward SF Zoo
            destinations = ['SF Zoo', 'Taraval/46th', 'Sunset Blvd']

        demo_arrivals = [
            {
                'destination': destinations[0],
                'minutes': 3,
                'vehicle': 'L1234',
                'time': (now + timedelta(minutes=3)).strftime('%H:%M')
            },
            {
                'destination': destinations[1] if len(destinations) > 1 else destinations[0],
                'minutes': 8,
                'vehicle': 'L5678',
                'time': (now + timedelta(minutes=8)).strftime('%H:%M')
            },
            {
                'destination': destinations[0],
                'minutes': 15,
                'vehicle': 'L9012',
                'time': (now + timedelta(minutes=15)).strftime('%H:%M')
            }
        ]
        self.last_update = now
        return demo_arrivals
    
    def create_text_pixels(self, text):
        """Create pixel representation of text using simple 5x7 font."""
        # Simplified font for key characters
        font_patterns = {
            'L': [[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            'T': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            'A': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'R': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
            'V': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,1,0,1,0],[0,0,1,0,0]],
            'E': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            'M': [[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'I': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]],
            'N': [[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'U': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'W': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,0,1,0,1],[1,1,0,1,1],[1,0,0,0,1]],
            'O': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'C': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,1],[0,1,1,1,0]],
            'D': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],
            'P': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
            '0': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,1,1],[1,0,1,0,1],[1,1,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '1': [[0,0,1,0,0],[0,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0]],
            '2': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,1,1,1,1]],
            '3': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '4': [[0,0,0,1,0],[0,0,1,1,0],[0,1,0,1,0],[1,0,0,1,0],[1,1,1,1,1],[0,0,0,1,0],[0,0,0,1,0]],
            '5': [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,1,0],[0,0,0,0,1],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '6': [[0,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '7': [[1,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[0,1,0,0,0],[0,1,0,0,0]],
            '8': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '9': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[0,0,0,0,1],[0,1,1,1,0]],
            '-': [[0,0],[0,0],[0,0],[1,1],[0,0],[0,0],[0,0]],  # Thin dash (2 pixels wide)
            ':': [[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            ' ': [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]  # Thinner space (2 pixels wide)
        }
        
        text_pixels = []
        for char in text.upper():
            if char in font_patterns:
                text_pixels.append(font_patterns[char])
            else:
                text_pixels.append(font_patterns[' '])
        
        return text_pixels

    def get_text_width(self, text_pixels):
        """Calculate the total width of text including variable-width characters."""
        total_width = 0
        for i, char_pixels in enumerate(text_pixels):
            char_width = len(char_pixels[0])
            total_width += char_width
            if i < len(text_pixels) - 1:  # Add space between characters (except last)
                total_width += 1
        return total_width

    def truncate_text_to_fit(self, text, max_width):
        """Truncate text to fit within the specified width."""
        # Try the full text first
        full_pixels = self.create_text_pixels(text)
        if self.get_text_width(full_pixels) <= max_width:
            return text

        # If it doesn't fit, try progressively shorter versions
        for i in range(len(text) - 1, 0, -1):
            truncated = text[:i]
            truncated_pixels = self.create_text_pixels(truncated)
            if self.get_text_width(truncated_pixels) <= max_width:
                return truncated

        # If even a single character doesn't fit, return empty string
        return ""

    def load_test_data(self):
        """Load test data from muni_test.txt file."""
        test_file = os.path.join(os.path.dirname(__file__), 'muni_test.txt')
        try:
            with open(test_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            data = json.loads(line)
                            self.test_data.append(data)
                        except json.JSONDecodeError as e:
                            print(f"⚠️  Invalid JSON in test data: {line[:50]}...")
            print(f"📋 Loaded {len(self.test_data)} test data entries")
        except FileNotFoundError:
            print(f"❌ Test file not found: {test_file}")
            print("📝 Create muni_test.txt with JSON test data")
            self.test_mode = False
        except Exception as e:
            print(f"❌ Error loading test data: {e}")
            self.test_mode = False

    def get_test_data(self):
        """Get next test data entry and convert to arrival format."""
        if not self.test_data:
            print("❌ No test data available")
            return []

        # Get current test data entry
        test_entry = self.test_data[self.test_data_index]
        current_index = self.test_data_index + 1  # Display 1-based index

        print(f"📋 Using test data entry {current_index}/{len(self.test_data)}")

        # Advance to next entry for next time
        self.test_data_index = (self.test_data_index + 1) % len(self.test_data)

        # Convert 511 API format to our internal format
        arrivals = []
        try:
            service_delivery = test_entry.get('ServiceDelivery', {})
            stop_monitoring = service_delivery.get('StopMonitoringDelivery', [])

            if stop_monitoring:
                monitored_visits = stop_monitoring[0].get('MonitoredStopVisit', [])

                for visit in monitored_visits:
                    journey = visit.get('MonitoredVehicleJourney', {})
                    call = journey.get('MonitoredCall', {})

                    if 'ExpectedArrivalTime' in call:
                        arrival_time_str = call['ExpectedArrivalTime']
                        arrival_time = datetime.fromisoformat(arrival_time_str.replace('Z', '+00:00'))
                        now = datetime.now(arrival_time.tzinfo)

                        minutes = max(0, int((arrival_time - now).total_seconds() / 60))
                        destination = journey.get('DestinationName', 'Unknown')

                        arrivals.append({
                            'minutes': minutes,
                            'destination': destination
                        })

        except Exception as e:
            print(f"❌ Error parsing test data: {e}")
            return []

        return arrivals

    def get_arrival_text_and_color(self):
        """Get the current arrival text and appropriate color."""
        if not self.current_arrivals or len(self.current_arrivals) == 0:
            return "NO DATA", (255, 255, 0)

        minutes = self.current_arrivals[0]['minutes']
        if minutes == 0:
            return "NOW", (255, 0, 0)  # Red - immediate/urgent
        elif minutes == 1:
            return "1 MIN", (255, 0, 0)  # Red - immediate/urgent
        elif minutes <= 5:
            return f"{minutes} MIN", (255, 128, 0)  # Orange - soon
        else:
            return f"{minutes} MIN", (0, 255, 0)  # Green - later

    def start_update_animation(self, is_initial_load=False):
        """Start the train animation for bringing in new arrival data."""
        self.animation_active = True
        self.animation_frame = 0

        if self.debug_mode:
            print("🎬 Switching to ANIMATION MODE (20 FPS)")

        # If there's already a train parked (not initial load), start with exit animation
        if not is_initial_load and hasattr(self, 'old_arrival_text') and self.old_arrival_text:
            self.animation_phase = "exiting"
            print("🚂 Train animation started - old train exiting, new train incoming!")
        else:
            self.animation_phase = "entering"
            print("🚂 Train animation started - towing next arrival time!")

    def draw_train_image(self, x, y):
        """Draw a pixel art MUNI train car facing left with classic grey/red colors."""
        # MUNI train car (16x8 pixels) - facing left
        # 0 = empty, 1 = grey body, 2 = red stripe, 3 = black windows
        train_pattern = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # Row 0
            [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],  # Row 1 - Top of car (grey)
            [2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],  # Row 2 - Car body (grey) with red left edge
            [2,3,1,1,3,3,1,3,3,1,3,3,1,3,3,0],  # Row 3 - Windows (narrow front window, bigger passenger windows)
            [2,3,1,1,3,3,1,3,3,1,3,3,1,3,3,0],  # Row 4 - Windows (narrow front window, bigger passenger windows)
            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0],  # Row 5 - Red stripe (within car body)
            [0,1,0,0,1,1,1,1,1,1,1,1,0,0,1,0],  # Row 6 - Bottom with wheels (grey)
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # Row 7
        ]

        # MUNI colors
        grey_color = (160, 160, 160)    # Light grey for train body
        red_color = (220, 20, 60)       # MUNI red stripe
        black_color = (0, 0, 0)         # Black windows

        # Draw the train with appropriate colors
        for row in range(len(train_pattern)):
            for col in range(len(train_pattern[row])):
                pixel_value = train_pattern[row][col]
                if pixel_value > 0:
                    pixel_x = x + col
                    pixel_y = y + row
                    if 0 <= pixel_x < 64 and 0 <= pixel_y < 32:
                        if pixel_value == 1:  # Grey body
                            color = grey_color
                        elif pixel_value == 2:  # Red stripe
                            color = red_color
                        elif pixel_value == 3:  # Black windows
                            color = black_color

                        self.controller.canvas.SetPixel(
                            pixel_x, pixel_y,
                            color[0], color[1], color[2]
                        )

    def draw_animated_train_update(self):
        """Draw the animated train towing arrival times across the screen."""
        if self.animation_phase == "exiting":
            # Old train exits from parked position to off-screen left
            progress = self.animation_frame / (self.animation_total_frames // 2)  # Half duration for exit
            start_x = 1   # Start from parked position
            end_x = -20   # Exit off-screen left
            train_x = int(start_x - ((start_x - end_x) * progress))

            # Use old arrival text and preserve original color
            arrival_text = self.old_arrival_text
            text_color = self.old_arrival_color  # Preserve original color during exit

        else:  # entering phase
            # New train enters from right and parks at left
            if self.animation_phase == "entering" and self.animation_frame == 0:
                # Just switched to entering phase, reset frame count
                pass

            # Calculate progress for entering phase
            if self.animation_phase == "entering":
                if hasattr(self, 'old_arrival_text') and self.old_arrival_text:
                    # This is a subsequent update with exit phase - use second half of animation
                    enter_start_frame = self.animation_total_frames // 2
                    progress = (self.animation_frame - enter_start_frame) / (self.animation_total_frames // 2)
                else:
                    # This is initial load - use full duration
                    progress = self.animation_frame / self.animation_total_frames
            else:
                progress = self.animation_frame / self.animation_total_frames

            start_x = 64  # Start off-screen right
            end_x = 1     # End at left edge with 1-pixel buffer
            train_x = int(start_x - ((start_x - end_x) * progress))

            # Use persistent display state
            arrival_text = self.display_arrival_text
            text_color = self.display_arrival_color

        # Use the arrival text determined by the animation phase
        next_arrival_text = arrival_text

        # Calculate positioning with train aligned with text (moved up)
        text_y = 12      # Text position (moved up from 18)
        train_y = text_y  # Train aligned with text

        # Draw the moving train
        self.draw_train_image(train_x, train_y)

        # Draw arrival time being towed behind the train
        if train_x < 80:  # Only show text when train is partially visible
            arrival_pixels = self.create_text_pixels(next_arrival_text)
            text_x = train_x + 18  # Position text behind the train (train is 16px wide)

            # Only draw text if it's on screen
            if text_x < 64:
                self.draw_text_pixels(arrival_pixels, text_x, text_y, text_color)  # Color-coded text

        # Advance animation
        self.animation_frame += 1
        if self.animation_frame % 20 == 0:  # Debug every 20 frames
            print(f"🎬 Animation {self.animation_phase} frame {self.animation_frame}/{self.animation_total_frames} (train at x={train_x})")

        # Handle phase transitions
        if self.animation_phase == "exiting" and self.animation_frame >= self.animation_total_frames // 2:
            # Switch to entering phase
            self.animation_phase = "entering"
            self.animation_frame = self.animation_total_frames // 2  # Start entering phase
            print("🔄 Switching to entering phase - new train incoming!")
        elif self.animation_frame >= self.animation_total_frames:
            # Animation complete
            self.animation_active = False
            self.animation_frame = 0
            self.animation_phase = "entering"  # Reset for next time

            # Store current arrival text and color for next exit animation
            if self.current_arrivals and len(self.current_arrivals) > 0:
                self.old_arrival_text = self.display_arrival_text
                self.old_arrival_color = self.display_arrival_color

            print("🚂 Train animation completed!")
            if self.debug_mode:
                print("🖼️  Switching to STATIC MODE (5s updates)")

    def display_arrivals(self):
        """Display arrival information on the matrix."""
        current_time = time.time()

        # Check if it's time to fetch new data (based on configured interval)
        should_fetch_data = (
            not self.animation_active and  # Don't fetch during animation
            (self.last_data_fetch_time == 0 or  # Initial load
             current_time - self.last_data_fetch_time >= self.update_interval)  # Interval elapsed
        )

        if should_fetch_data:
            if self.test_mode:
                arrivals = self.get_test_data()
            else:
                arrivals = self.get_demo_data()  # Using demo data for now

            # Check if this is new data (different from current) or initial load
            is_new_data = arrivals != self.current_arrivals
            is_initial_load = len(self.current_arrivals) == 0

            # Update current arrivals and timing
            self.current_arrivals = arrivals
            self.last_data_fetch_time = current_time

            # Update persistent display state with new data
            if arrivals and len(arrivals) > 0:
                self.display_arrival_text, self.display_arrival_color = self.get_arrival_text_and_color()
                if self.debug_mode:
                    print(f"📱 Display updated: {self.display_arrival_text}")
            else:
                self.display_arrival_text = "NO DATA"
                self.display_arrival_color = (255, 255, 0)
                if self.debug_mode:
                    print(f"📱 Display updated: NO DATA")

            # ALWAYS set next update time when we fetch data (respects update_interval)
            self.next_update_time = current_time + self.update_interval
            if self.debug_mode:
                print(f"📊 Data fetched at {time.strftime('%H:%M:%S')}, next fetch in {self.update_interval}s")
                print(f"📊 New data: {is_new_data}, Initial load: {is_initial_load}")
        else:
            # Use existing data - no changes to display state
            arrivals = self.current_arrivals
            is_new_data = False
            is_initial_load = False

        # Test trigger: Force animation 30 seconds after startup
        current_time = time.time()
        is_test_trigger = (current_time - self.start_time > 29 and
                          current_time - self.start_time < 35 and
                          not self.animation_active)

        # Debug: Print timing info
        if current_time - self.start_time > 29 and current_time - self.start_time < 35:
            print(f"🕐 Debug: {current_time - self.start_time:.1f}s since startup, test_trigger={is_test_trigger}")

        if not arrivals:
            self.display_no_data()
            return

        # Start animation for new data, initial load, or test trigger
        if (is_new_data or is_initial_load) and not self.animation_active:
            self.start_update_animation(is_initial_load=is_initial_load)
        elif is_test_trigger:
            print("🧪 Test trigger: Starting animation 30 seconds after startup!")
            self.start_update_animation(is_initial_load=False)
        
        # Display format: "L-TARAVAL  3min  8min  15min"
        if hasattr(self.controller, 'canvas') and self.controller.canvas:
            self.controller.clear()
            
            # Direction indicator in top right (with 1 pixel margin from edge)
            direction_pixels = self.create_text_pixels(self.direction_display)
            direction_width = self.get_text_width(direction_pixels)
            direction_x = 64 - direction_width - 1
            self.draw_text_pixels(direction_pixels, direction_x, 2, (255, 255, 255))

            # Header: Line name in official MUNI line color
            # Calculate available space for header (leave 2 pixels gap between header and direction)
            available_width = direction_x - 1 - 2  # Start at x=1, leave 2px gap before direction
            header_text = self.truncate_text_to_fit(self.line_name, available_width)
            header_pixels = self.create_text_pixels(header_text)
            self.draw_text_pixels(header_pixels, 1, 2, self.line_color)

            # Arrival times are shown via animation only
            # No static display - users see arrival info when train delivers it
            
            # Handle train animation or static display
            if self.animation_active:
                self.draw_animated_train_update()
            else:
                # Static mode: Show train parked on left with arrival information
                if self.display_arrival_text != "NO DATA":
                    # Draw train parked at left edge (same position as end of animation)
                    train_x = 1  # Parked position
                    train_y = 12  # Same y position as during animation
                    self.draw_train_image(train_x, train_y)

                    # Draw arrival time next to the parked train
                    arrival_pixels = self.create_text_pixels(self.display_arrival_text)
                    text_x = train_x + 17  # Position text after train (train is 16 pixels wide, +1 for gap)
                    text_y = train_y  # Same y position as train

                    self.draw_text_pixels(arrival_pixels, text_x, text_y, self.display_arrival_color)

                # Update timestamp at bottom left
                if self.last_update:
                    update_text = f"UPD {self.last_update.strftime('%H:%M')}"
                    update_pixels = self.create_text_pixels(update_text)
                    self.draw_text_pixels(update_pixels, 1, 25, (100, 100, 100))

            # Always draw countdown timer at bottom right
            self.draw_countdown_timer()

            self.controller.canvas = self.controller.matrix.SwapOnVSync(self.controller.canvas)
    
    def draw_text_pixels(self, text_pixels, start_x, start_y, color):
        """Draw text pixels on the canvas."""
        char_x = start_x

        for char_pixels in text_pixels:
            char_width = len(char_pixels[0])  # Get actual width of this character
            for y in range(7):
                for x in range(char_width):
                    if char_pixels[y][x] == 1:
                        pixel_x = char_x + x
                        pixel_y = start_y + y

                        if 0 <= pixel_x < 64 and 0 <= pixel_y < 32:
                            self.controller.canvas.SetPixel(
                                pixel_x, pixel_y,
                                color[0], color[1], color[2]
                            )

            char_x += char_width + 1  # Move to next character position (character width + 1 space)
    
    def display_no_data(self):
        """Display when no arrival data is available."""
        if hasattr(self.controller, 'canvas') and self.controller.canvas:
            self.controller.clear()
            
            no_data_pixels = self.create_text_pixels("NO DATA")
            self.draw_text_pixels(no_data_pixels, 10, 12, (255, 0, 0))
            
            self.controller.canvas = self.controller.matrix.SwapOnVSync(self.controller.canvas)

    def draw_countdown_timer(self):
        """Draw countdown timer showing time to next update."""
        if self.next_update_time is None:
            return

        current_time = time.time()
        seconds_remaining = max(0, int(self.next_update_time - current_time))

        if seconds_remaining > 0:
            countdown_text = f"UPD {seconds_remaining}s"
        else:
            countdown_text = "UPD NOW"

        # Debug output every 10 seconds for countdown
        if hasattr(self, '_last_countdown_debug'):
            if current_time - self._last_countdown_debug > 10:
                print(f"⏰ Countdown: {countdown_text} (next update in {seconds_remaining}s)")
                self._last_countdown_debug = current_time
        else:
            self._last_countdown_debug = current_time

        # Draw countdown in grey at bottom right
        countdown_pixels = self.create_text_pixels(countdown_text)
        text_width = self.get_text_width(countdown_pixels)
        x_pos = 64 - text_width - 1  # Right-aligned with 1-pixel margin
        y_pos = 25  # Bottom of display

        # Grey color for countdown
        grey_color = (64, 64, 64)
        self.draw_text_pixels(countdown_pixels, x_pos, y_pos, grey_color)

    def run_display(self):
        """Run the continuous MUNI display."""
        print(f"🚇 MUNI {self.line_name} Real-time Display")
        print("=" * 40)
        print(f"🚂 Line: {self.line_name} (ID: {self.line_id})")
        print(f"📍 Stop: {self.current_stop}")
        print(f"🧭 Direction: {self.direction} ({self.direction_display})")
        print(f"🎨 Line Color: RGB{self.line_color}")
        print("🌐 Emulator URL: http://localhost:8888/")
        print(f"⏱️  Data Update Interval: {self.update_interval} seconds")
        print("🎬 Display Update: 20 FPS during animation, 5s when static")
        
        if self.test_mode:
            print("🧪 Using test mode data from muni_test.txt")
        elif self.api_key == "YOUR_511_API_KEY_HERE":
            print("⚠️  Using demo data (no API key configured)")
            self.get_api_key_instructions()
        else:
            print("✅ Using live MUNI data")
        
        print("Press Ctrl+C to stop")
        print()
        
        self.running = True
        
        try:
            while self.running:
                print(f"🔄 Updating arrivals... ({datetime.now().strftime('%H:%M:%S')})")
                self.display_arrivals()

                # Two-mode update system
                if self.animation_active:
                    # Animation mode: High frequency for smooth FPS (20 FPS = 0.05s)
                    time.sleep(0.05)
                else:
                    # Static mode: Update display every 5 seconds for responsiveness
                    time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 MUNI display stopped by user")
        finally:
            self.running = False
            self.controller.stop()
            self.controller.clear()
            print("\n🎉 Thanks for using the MUNI L-Taraval display!")


def main():
    """Run the MUNI L-Taraval display."""
    # Load API key from environment variable, config file, or use default
    config_file = "examples/muni.config"
    api_key = os.environ.get('MUNI_API_KEY')

    # If no environment variable, try to load from config file
    if not api_key or api_key == 'YOUR_511_API_KEY_HERE':
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('MUNI_API_KEY='):
                            api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            break
        except Exception as e:
            print(f"⚠️  Error reading API key from config: {e}")

    # Fallback to default if still not found
    if not api_key:
        api_key = 'YOUR_511_API_KEY_HERE'

    display = MuniLTaravalDisplay(api_key=api_key, config_file=config_file)
    display.run_display()


if __name__ == "__main__":
    main()
