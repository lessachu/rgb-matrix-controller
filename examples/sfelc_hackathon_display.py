#!/usr/bin/env python3
"""
SFELC 2025 AI Hackathon Display
Displays "Hello SFELC 2025 AI Hackathon!" scrolling across the 64x32 RGB matrix.
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from matrix.emulator_controller import EmulatorController


def main():
    """Display the SFELC 2025 AI Hackathon message."""
    print("🚀 SFELC 2025 AI Hackathon Display")
    print("=" * 40)
    print("🎯 Message: 'Hello SFELC 2025 AI Hackathon!'")
    print("🌐 Emulator URL: http://localhost:8888/")
    print("Press Ctrl+C to stop")
    print()
    
    # Initialize the emulator controller
    controller = EmulatorController(use_emulator=True)
    
    # The hackathon message
    message = "Hello SFELC 2025 AI Hackathon!"
    
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
        print("🎨 Starting hackathon display...")
        print("   The message will scroll continuously with changing colors")
        
        color_index = 0
        
        while True:
            # Get current color
            current_color = colors[color_index % len(colors)]
            
            print(f"📱 Displaying in color: RGB{current_color}")
            
            # Display scrolling text
            controller.display_text(
                message, 
                color=current_color, 
                scroll=True
            )
            
            # Let it scroll for a while (about 3 full cycles)
            time.sleep(12)
            
            # Stop current scrolling
            controller.stop()
            
            # Brief pause between color changes
            time.sleep(0.5)
            
            # Move to next color
            color_index += 1
            
    except KeyboardInterrupt:
        print("\n🛑 Hackathon display stopped by user")
    finally:
        controller.stop()
        controller.clear()
        print("\n🎉 Thanks for checking out the SFELC 2025 AI Hackathon display!")
        print("💡 Your 64x32 RGB matrix is ready for the hackathon!")


if __name__ == "__main__":
    main()
