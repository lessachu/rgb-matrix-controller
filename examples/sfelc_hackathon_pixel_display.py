#!/usr/bin/env python3
"""
SFELC 2025 AI Hackathon Pixel Display
Displays "Hello SFELC 2025 AI Hackathon!" using pixel-based scrolling.
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from matrix.emulator_controller import EmulatorController


def create_text_pixels(text):
    """Create a pixel representation of text using a simple 5x7 font."""
    # Simple 5x7 font patterns for basic characters
    font_patterns = {
        'H': [
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1]
        ],
        'E': [
            [1,1,1,1,1],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,1]
        ],
        'L': [
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,1]
        ],
        'O': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0]
        ],
        'S': [
            [0,1,1,1,1],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [0,1,1,1,0],
            [0,0,0,0,1],
            [0,0,0,0,1],
            [1,1,1,1,0]
        ],
        'F': [
            [1,1,1,1,1],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0]
        ],
        'C': [
            [0,1,1,1,1],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [0,1,1,1,1]
        ],
        'A': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,1,1,1,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1]
        ],
        'I': [
            [1,1,1,1,1],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [1,1,1,1,1]
        ],
        'T': [
            [1,1,1,1,1],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0]
        ],
        'K': [
            [1,0,0,0,1],
            [1,0,0,1,0],
            [1,0,1,0,0],
            [1,1,0,0,0],
            [1,0,1,0,0],
            [1,0,0,1,0],
            [1,0,0,0,1]
        ],
        'N': [
            [1,0,0,0,1],
            [1,1,0,0,1],
            [1,0,1,0,1],
            [1,0,0,1,1],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [1,0,0,0,1]
        ],
        '2': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,1,0,0],
            [0,1,0,0,0],
            [1,1,1,1,1]
        ],
        '0': [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,1,1],
            [1,0,1,0,1],
            [1,1,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0]
        ],
        '5': [
            [1,1,1,1,1],
            [1,0,0,0,0],
            [1,1,1,1,0],
            [0,0,0,0,1],
            [0,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0]
        ],
        '!': [
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,0,0,0],
            [0,0,1,0,0]
        ],
        ' ': [
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0]
        ]
    }
    
    # Convert text to pixel array
    text_pixels = []
    for char in text.upper():
        if char in font_patterns:
            text_pixels.append(font_patterns[char])
        else:
            # Use space for unknown characters
            text_pixels.append(font_patterns[' '])
    
    return text_pixels


def main():
    """Display the SFELC 2025 AI Hackathon message using pixels."""
    print("🚀 SFELC 2025 AI Hackathon Pixel Display")
    print("=" * 45)
    print("🎯 Message: 'Hello SFELC 2025 AI Hackathon!'")
    print("🌐 Emulator URL: http://localhost:8888/")
    print("Press Ctrl+C to stop")
    print()
    
    # Initialize the emulator controller
    controller = EmulatorController(use_emulator=True)
    
    # The hackathon message
    message = "HELLO SFELC 2025 AI HACKATHON!"
    
    # Create pixel representation
    text_pixels = create_text_pixels(message)
    
    # Calculate total width (5 pixels per char + 1 space between chars)
    total_width = len(text_pixels) * 6 - 1
    
    # Bright, eye-catching colors for the hackathon
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green  
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 128, 0),  # Orange
        (128, 255, 0),  # Lime
    ]
    
    try:
        print("🎨 Starting hackathon pixel display...")
        print("   The message will scroll continuously with changing colors")
        
        color_index = 0
        scroll_position = 64  # Start from right edge
        
        while True:
            # Get current color
            current_color = colors[color_index % len(colors)]
            
            # Clear the display
            controller.clear()
            
            if hasattr(controller, 'canvas') and controller.canvas:
                # Draw the text at current scroll position
                char_x = scroll_position
                
                for char_pixels in text_pixels:
                    # Draw each character
                    for y in range(7):  # 7 rows in font
                        for x in range(5):  # 5 columns in font
                            if char_pixels[y][x] == 1:
                                pixel_x = char_x + x
                                pixel_y = 12 + y  # Center vertically (32/2 - 7/2 ≈ 12)
                                
                                # Only draw if pixel is visible on screen
                                if 0 <= pixel_x < 64 and 0 <= pixel_y < 32:
                                    controller.canvas.SetPixel(
                                        pixel_x, pixel_y, 
                                        current_color[0], current_color[1], current_color[2]
                                    )
                    
                    char_x += 6  # Move to next character position (5 + 1 space)
                
                # Update the display
                controller.canvas = controller.matrix.SwapOnVSync(controller.canvas)
            
            # Move scroll position
            scroll_position -= 1
            
            # Reset scroll when text has completely passed
            if scroll_position < -total_width:
                scroll_position = 64
                color_index += 1  # Change color when text loops
                print(f"📱 Switching to color: RGB{colors[color_index % len(colors)]}")
            
            # Control scroll speed
            time.sleep(0.08)  # Adjust for desired scroll speed
            
    except KeyboardInterrupt:
        print("\n🛑 Hackathon display stopped by user")
    finally:
        controller.stop()
        controller.clear()
        print("\n🎉 Thanks for checking out the SFELC 2025 AI Hackathon display!")
        print("💡 Your 64x32 RGB matrix is ready for the hackathon!")


if __name__ == "__main__":
    main()
