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

    def display_arrivals(self):
        """Display arrival information on the matrix."""
        arrivals = self.get_demo_data()  # Using demo data for now
        
        if not arrivals:
            self.display_no_data()
            return
        
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

            # Arrival times
            y_pos = 12
            colors = [(255, 0, 0), (255, 128, 0), (0, 255, 255)]  # Red, Orange, Cyan
            
            for i, arrival in enumerate(arrivals[:3]):
                if arrival['minutes'] == 0:
                    text = "NOW"
                elif arrival['minutes'] == 1:
                    text = "1MIN"
                else:
                    text = f"{arrival['minutes']}MIN"
                
                text_pixels = self.create_text_pixels(text)
                x_pos = 2 + (i * 20)  # Space arrivals across the display
                text_width = self.get_text_width(text_pixels)

                if x_pos + text_width <= 64:  # Make sure it fits
                    self.draw_text_pixels(text_pixels, x_pos, y_pos, colors[i])
            
            # Update timestamp at bottom
            if self.last_update:
                update_text = f"UPD {self.last_update.strftime('%H:%M')}"
                update_pixels = self.create_text_pixels(update_text)
                self.draw_text_pixels(update_pixels, 1, 25, (100, 100, 100))
            
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
    
    def run_display(self):
        """Run the continuous MUNI display."""
        print(f"🚇 MUNI {self.line_name} Real-time Display")
        print("=" * 40)
        print(f"🚂 Line: {self.line_name} (ID: {self.line_id})")
        print(f"📍 Stop: {self.current_stop}")
        print(f"🧭 Direction: {self.direction} ({self.direction_display})")
        print(f"🎨 Line Color: RGB{self.line_color}")
        print("🌐 Emulator URL: http://localhost:8888/")
        
        if self.api_key == "YOUR_511_API_KEY_HERE":
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
                
                # Update every 30 seconds
                time.sleep(30)
                
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
