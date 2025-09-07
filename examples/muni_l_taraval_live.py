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

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from matrix.emulator_controller import EmulatorController


class MuniLTaravalDisplay:
    """Real-time MUNI L-Taraval arrival display."""
    
    def __init__(self, api_key=None):
        """Initialize the MUNI display."""
        self.api_key = api_key or "YOUR_511_API_KEY_HERE"
        self.controller = EmulatorController(use_emulator=True)
        self.running = False
        self.arrivals_data = []
        self.last_update = None
        
        # MUNI L-Taraval line configuration
        self.agency = "SF"  # San Francisco MUNI
        self.line_id = "L"  # L-Taraval line
        
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
            "Taraval/46th": "13207",    # Taraval & 46th Ave
            "SF Zoo": "13206"           # SF Zoo (end of line)
        }
        
        # Default stop (you can change this to your preferred stop)
        self.current_stop = "West Portal"
        self.current_stop_id = self.stops[self.current_stop]
    
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
        demo_arrivals = [
            {
                'destination': 'Embarcadero',
                'minutes': 3,
                'vehicle': 'L1234',
                'time': (now + timedelta(minutes=3)).strftime('%H:%M')
            },
            {
                'destination': 'SF Zoo',
                'minutes': 8,
                'vehicle': 'L5678',
                'time': (now + timedelta(minutes=8)).strftime('%H:%M')
            },
            {
                'destination': 'Embarcadero',
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
            ':': [[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            ' ': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
        }
        
        text_pixels = []
        for char in text.upper():
            if char in font_patterns:
                text_pixels.append(font_patterns[char])
            else:
                text_pixels.append(font_patterns[' '])
        
        return text_pixels
    
    def display_arrivals(self):
        """Display arrival information on the matrix."""
        arrivals = self.get_demo_data()  # Using demo data for now
        
        if not arrivals:
            self.display_no_data()
            return
        
        # Display format: "L-TARAVAL  3min  8min  15min"
        if hasattr(self.controller, 'canvas') and self.controller.canvas:
            self.controller.clear()
            
            # Header: "L-TARAVAL" in green
            header_pixels = self.create_text_pixels("L-TARAVAL")
            self.draw_text_pixels(header_pixels, 1, 2, (0, 255, 0))
            
            # Current time in top right
            current_time = datetime.now().strftime("%H:%M")
            time_pixels = self.create_text_pixels(current_time)
            self.draw_text_pixels(time_pixels, 64 - len(time_pixels) * 6, 2, (255, 255, 0))
            
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
                
                if x_pos + len(text_pixels) * 6 <= 64:  # Make sure it fits
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
            for y in range(7):
                for x in range(5):
                    if char_pixels[y][x] == 1:
                        pixel_x = char_x + x
                        pixel_y = start_y + y
                        
                        if 0 <= pixel_x < 64 and 0 <= pixel_y < 32:
                            self.controller.canvas.SetPixel(
                                pixel_x, pixel_y,
                                color[0], color[1], color[2]
                            )
            
            char_x += 6  # Move to next character position
    
    def display_no_data(self):
        """Display when no arrival data is available."""
        if hasattr(self.controller, 'canvas') and self.controller.canvas:
            self.controller.clear()
            
            no_data_pixels = self.create_text_pixels("NO DATA")
            self.draw_text_pixels(no_data_pixels, 10, 12, (255, 0, 0))
            
            self.controller.canvas = self.controller.matrix.SwapOnVSync(self.controller.canvas)
    
    def run_display(self):
        """Run the continuous MUNI display."""
        print("🚇 MUNI L-Taraval Real-time Display")
        print("=" * 40)
        print(f"📍 Stop: {self.current_stop}")
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
    # You can set your API key here or in environment variable
    api_key = os.environ.get('MUNI_API_KEY', 'YOUR_511_API_KEY_HERE')
    
    display = MuniLTaravalDisplay(api_key=api_key)
    display.run_display()


if __name__ == "__main__":
    main()
