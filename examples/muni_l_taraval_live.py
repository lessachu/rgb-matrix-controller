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

        # Load line ID from config, or extract from line name
        config_line_id = self.config.get('LINE_ID', '')
        if config_line_id:
            self.line_id = config_line_id
        else:
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
        config_stop_id = self.config.get('STOP_ID', '')

        if config_stop_id:
            # Use stop ID directly from config
            self.stop_id = config_stop_id
            self.current_stop = config_stop_name
        else:
            # Use stop name lookup (legacy method)
            self.current_stop = config_stop_name if config_stop_name in self.stops else "Taraval/17th"
            self.stop_id = self.stops[self.current_stop]

        # Load direction from config file, fallback to default
        config_direction = self.config.get('DIRECTION', 'Inbound')
        self.direction = config_direction
        self.direction_id = 1 if config_direction.lower() == 'inbound' else 0
        self.direction_display = "I" if config_direction.lower() == 'inbound' else "O"

        # Animation state for train towing updates
        self.animation_active = False
        self.animation_frame = 0
        self.animation_total_frames = 120  # Default frames, will be calculated dynamically
        self.animation_phase = "entering"  # "exiting" or "entering"
        self.current_arrivals = []  # Track current arrivals to detect changes
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

        # Track previous animation positions for selective clearing
        self.prev_train_x = None
        self.prev_text_x = None
        self.prev_text_width = None

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
        print("   4. Add to examples/muni.config: MUNI_API_KEY=your_key")
        print("   5. Or set environment variable: export MUNI_API_KEY=your_key")
        print()

    def get_live_data(self):
        """Fetch live arrival data from 511.org API."""
        if not self.api_key:
            print("❌ No API key available - falling back to demo data")
            return self.get_demo_data()

        try:
            # 511.org API endpoint for real-time arrivals
            url = "http://api.511.org/transit/StopMonitoring"

            params = {
                'api_key': self.api_key,
                'agency': 'SF',  # San Francisco (MUNI)
                'stopCode': self.stop_id,
                'format': 'json'
            }

            if self.debug_mode:
                print(f"🌐 Fetching live data from 511.org API...")
                print(f"   Stop ID: {self.stop_id}")
                print(f"   Agency: SF (MUNI)")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            # Handle UTF-8 BOM if present
            response_text = response.text
            if response_text.startswith('\ufeff'):
                response_text = response_text[1:]  # Remove BOM

            data = json.loads(response_text)

            if self.debug_mode:
                print(f"✅ API response received ({len(str(data))} chars)")
                # Print first level of response structure for debugging
                if isinstance(data, dict):
                    print(f"🔍 Response keys: {list(data.keys())}")

            # Parse the 511.org API response
            arrivals = self.parse_511_response(data)

            if arrivals:
                if self.debug_mode:
                    print(f"📊 Parsed {len(arrivals)} arrivals from live data")
                return arrivals
            else:
                print("⚠️  No arrivals found in API response - using demo data")
                return self.get_demo_data()

        except requests.exceptions.Timeout:
            print("⚠️  API request timed out - using demo data")
            return self.get_demo_data()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  API request failed: {e} - using demo data")
            return self.get_demo_data()
        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON response: {e} - using demo data")
            return self.get_demo_data()
        except Exception as e:
            print(f"⚠️  Unexpected error: {e} - using demo data")
            return self.get_demo_data()

    def parse_511_response(self, data):
        """Parse 511.org API response into our internal arrival format."""
        arrivals = []

        try:
            service_delivery = data.get('ServiceDelivery', {})
            stop_monitoring = service_delivery.get('StopMonitoringDelivery', [])

            if not stop_monitoring:
                if self.debug_mode:
                    print("⚠️  No StopMonitoringDelivery in API response")
                    print(f"🔍 ServiceDelivery keys: {list(service_delivery.keys())}")
                return arrivals

            # Get the first (and usually only) stop monitoring delivery
            delivery = stop_monitoring[0] if isinstance(stop_monitoring, list) else stop_monitoring
            monitored_calls = delivery.get('MonitoredStopVisit', [])

            if not monitored_calls:
                if self.debug_mode:
                    print("⚠️  No MonitoredStopVisit in API response")
                    print(f"🔍 Delivery keys: {list(delivery.keys())}")
                return arrivals

            if self.debug_mode:
                print(f"🔍 Found {len(monitored_calls)} monitored calls")

            for call in monitored_calls:
                try:
                    journey = call.get('MonitoredVehicleJourney', {})
                    line_ref = journey.get('LineRef', '')
                    direction_ref = journey.get('DirectionRef', '')

                    # Debug: Show what we're getting vs what we're looking for
                    if self.debug_mode:
                        print(f"🔍 Found: Line={line_ref}, Direction={direction_ref} (looking for Line={self.line_id}, Direction={self.direction})")

                    # Map direction to API format (Inbound -> IB, Outbound -> OB)
                    api_direction = "IB" if self.direction.lower() == "inbound" else "OB"

                    # Filter for our specific line and direction
                    if (line_ref == self.line_id and
                        direction_ref == api_direction):

                        monitored_call = journey.get('MonitoredCall', {})

                        # Get arrival time
                        expected_arrival = monitored_call.get('ExpectedArrivalTime')
                        aimed_arrival = monitored_call.get('AimedArrivalTime')

                        arrival_time_str = expected_arrival or aimed_arrival

                        if arrival_time_str:
                            # Parse ISO 8601 timestamp
                            arrival_time = datetime.fromisoformat(arrival_time_str.replace('Z', '+00:00'))

                            # Convert to local time and calculate minutes
                            now = datetime.now(arrival_time.tzinfo)
                            minutes_until = int((arrival_time - now).total_seconds() / 60)

                            if minutes_until >= 0:  # Only future arrivals
                                arrivals.append({
                                    'minutes': minutes_until,
                                    'destination': journey.get('DestinationName', 'Unknown'),
                                    'vehicle_id': journey.get('VehicleRef', ''),
                                    'line': line_ref,
                                    'direction': direction_ref
                                })

                except Exception as e:
                    if self.debug_mode:
                        print(f"⚠️  Error parsing arrival: {e}")
                    continue

            # Sort by arrival time
            arrivals.sort(key=lambda x: x['minutes'])

            if self.debug_mode and arrivals:
                arrival_times = [f"{a['minutes']}min" for a in arrivals[:3]]
                print(f"📋 Live arrivals: {arrival_times}")

        except Exception as e:
            if self.debug_mode:
                print(f"⚠️  Error parsing 511 response: {e}")

        return arrivals

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
        # Calculate required animation frames based on text lengths
        old_text_length = 0
        if hasattr(self, 'old_arrival_text') and self.old_arrival_text:
            old_text_pixels = self.create_text_pixels(self.old_arrival_text)
            old_text_length = self.get_text_width(old_text_pixels)
            print(f"🔍 Old text: '{self.old_arrival_text}' width: {old_text_length}px")

        new_text_pixels = self.create_text_pixels(self.display_arrival_text)
        new_text_length = self.get_text_width(new_text_pixels)
        print(f"🔍 New text: '{self.display_arrival_text}' width: {new_text_length}px")

        # Calculate frames needed to ensure complete text clearance
        self.animation_total_frames = self.calculate_animation_frames(old_text_length, new_text_length)
        print(f"🔍 Calculated frames: {self.animation_total_frames} (old_len={old_text_length}, new_len={new_text_length})")

        self.animation_active = True
        self.animation_frame = 0

        if self.debug_mode:
            print("🎬 Switching to ANIMATION MODE (20 FPS)")
            print(f"🎬 Animation duration: {self.animation_total_frames} frames ({self.animation_total_frames/20:.1f}s)")

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

    def clear_animation_area(self):
        """Selectively clear only the animation area and countdown timer to reduce flashing."""
        if hasattr(self.controller, 'canvas') and self.controller.canvas:
            # Clear the animation strip (where train and text move)
            animation_y_start = 12  # Start of animation area
            animation_y_end = 20    # End of animation area (train is 8 pixels tall)

            for y in range(animation_y_start, animation_y_end):
                for x in range(64):  # Full width
                    self.controller.canvas.SetPixel(x, y, 0, 0, 0)  # Set to black

            # Also clear the countdown timer area (bottom right)
            # Countdown is at y=25, and text is 7 pixels tall
            countdown_y_start = 25
            countdown_y_end = 32    # Bottom of display

            for y in range(countdown_y_start, countdown_y_end):
                for x in range(64):  # Full width to clear any previous countdown text
                    self.controller.canvas.SetPixel(x, y, 0, 0, 0)  # Set to black

    def redraw_static_elements(self):
        """Redraw static elements that might overlap with the animation area."""
        # The animation area is y=12-20, so we need to redraw any static elements in that range
        # In our case, the header and direction are at y=2, and countdown is at y=25+
        # So no static elements overlap with the animation area - this method can be empty for now
        pass

    def calculate_animation_frames(self, old_text_length, new_text_length):
        """Calculate the number of frames needed for complete animation."""
        if old_text_length == 0:
            # Initial load - new train enters from off-screen to x=1
            new_total_length = 16 + 2 + new_text_length
            new_start_x = 64 + new_total_length  # Start completely off-screen right
            distance = new_start_x - 1  # Distance to parked position
            return int(distance * 1)  # 1 frame per pixel

        # For updates: both trains move simultaneously
        # Old train: exits from x=1 to completely off-screen (including text)
        old_text_end_x = 1 + 18 + old_text_length  # Rightmost pixel of old text
        old_exit_distance = old_text_end_x - 0  # Distance to clear screen

        # New train: enters from off-screen to x=1
        new_total_length = 16 + 2 + new_text_length
        new_start_x = 64 + new_total_length  # Start completely off-screen right
        new_enter_distance = new_start_x - 1  # Distance to parked position

        # Use the maximum distance to ensure both animations complete
        max_distance = max(old_exit_distance, new_enter_distance)
        frames_needed = int(max_distance * 1) + 1  # 1 frame per pixel + 1 to ensure completion

        print(f"🔍 Animation calc: old_exit={old_exit_distance}px, new_enter={new_enter_distance}px, max={max_distance}px, frames={frames_needed}")
        return frames_needed

    def draw_animated_train_update(self):
        """Draw the animated train towing arrival times across the screen."""
        text_y = 12      # Text position
        train_y = text_y  # Train aligned with text

        # Calculate the effective length of train + text for proper spacing
        has_old_train = hasattr(self, 'old_arrival_text') and self.old_arrival_text

        if has_old_train:
            # Calculate old train + text length
            old_text_pixels = self.create_text_pixels(self.old_arrival_text)
            old_text_width = self.get_text_width(old_text_pixels)
            old_total_length = 16 + 2 + old_text_width  # train + gap + text
        else:
            old_total_length = 16  # Just train width

        # Calculate new train + text length
        new_text_pixels = self.create_text_pixels(self.display_arrival_text)
        new_text_width = self.get_text_width(new_text_pixels)
        new_total_length = 16 + 2 + new_text_width  # train + gap + text



        if self.animation_phase == "exiting":
            # Simple simultaneous animation: old train exits, new train enters
            progress = self.animation_frame / self.animation_total_frames

            # Old train exits from x=1 to completely off-screen
            old_start_x = 1
            old_end_x = -(old_total_length + 5)  # Exit with buffer
            old_train_x = int(old_start_x - ((old_start_x - old_end_x) * progress))

            # New train enters from off-screen to x=1
            new_start_x = 64 + new_total_length  # Start completely off-screen right
            new_end_x = 1  # End at parked position
            new_train_x = int(new_start_x - ((new_start_x - new_end_x) * progress))

            # Draw old train if still visible
            if old_train_x > -20:
                self.draw_train_image(old_train_x, train_y)

            # Draw old arrival text
            old_text_x = old_train_x + 18
            if old_text_x > -(old_text_width + 5):
                self.draw_text_pixels(old_text_pixels, old_text_x, text_y, self.old_arrival_color)

            # Draw new train if visible
            if new_train_x < 64:
                self.draw_train_image(new_train_x, train_y)

            # Draw new arrival text
            new_text_x = new_train_x + 18
            if new_text_x < 64 and new_train_x < 80:
                self.draw_text_pixels(new_text_pixels, new_text_x, text_y, self.display_arrival_color)

        elif self.animation_phase == "entering":
            # Single train animation for initial load
            enter_progress = self.animation_frame / self.animation_total_frames
            enter_start_x = 64 + new_total_length  # Start completely off-screen right
            enter_end_x = 1     # End at left edge
            new_train_x = int(enter_start_x - ((enter_start_x - enter_end_x) * enter_progress))

            # Draw new train if visible
            if new_train_x < 64:
                self.draw_train_image(new_train_x, train_y)

            # Draw new arrival text being towed
            new_text_x = new_train_x + 18  # Position text behind the train
            if new_text_x < 64 and new_train_x < 80:  # Only show text when train is partially visible
                self.draw_text_pixels(new_text_pixels, new_text_x, text_y, self.display_arrival_color)

        # Advance animation
        self.animation_frame += 1
        if self.animation_frame % 20 == 0:  # Debug every 20 frames
            print(f"🎬 Animation {self.animation_phase} frame {self.animation_frame}/{self.animation_total_frames}")

        # Handle animation completion (no more phase transitions)
        if self.animation_frame >= self.animation_total_frames:
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
                arrivals = self.get_live_data()  # Now using live 511.org API data!

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

        if not arrivals:
            self.display_no_data()
            return

        # Start animation for new data or initial load
        if (is_new_data or is_initial_load) and not self.animation_active:
            self.start_update_animation(is_initial_load=is_initial_load)
        
        # Display format: "L-TARAVAL  3min  8min  15min"
        if hasattr(self.controller, 'canvas') and self.controller.canvas:
            # Use selective clearing during animation to reduce flashing
            if self.animation_active:
                # Only clear the animation area during animation
                self.clear_animation_area()
                # Redraw static elements that might be in the animation area
                self.redraw_static_elements()
            else:
                # Full clear when not animating (less frequent)
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

                    # Draw arrival time next to the parked train (same positioning as animation)
                    arrival_pixels = self.create_text_pixels(self.display_arrival_text)
                    text_x = train_x + 18  # Position text behind train (same as animation: train + 2px gap)
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
    # Load API key from config file first, then environment variable, or use default
    config_file = "examples/muni.config"
    api_key = None

    # First, try to load from config file
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('MUNI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        if api_key and api_key != 'YOUR_511_API_KEY_HERE':
                            break
                        api_key = None  # Reset if placeholder value
    except Exception as e:
        print(f"⚠️  Error reading API key from config: {e}")

    # If no valid key from config file, try environment variable
    if not api_key:
        env_key = os.environ.get('MUNI_API_KEY')
        if env_key and env_key != 'YOUR_511_API_KEY_HERE':
            api_key = env_key

    # Fallback to default if still not found
    if not api_key:
        api_key = 'YOUR_511_API_KEY_HERE'

    display = MuniLTaravalDisplay(api_key=api_key, config_file=config_file)
    display.run_display()


if __name__ == "__main__":
    main()
