#!/usr/bin/env python3
"""
Hello World Example - Basic text display on RGB matrix.
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from matrix.controller import MatrixController


def main():
    """Run the hello world example."""
    print("🌈 RGB Matrix Hello World Example")
    print("=" * 40)
    
    # Initialize the matrix controller
    controller = MatrixController()
    
    try:
        # Display static text
        print("Displaying 'Hello World!' in white...")
        controller.display_text("Hello World!", color=(255, 255, 255))
        time.sleep(3)
        
        # Display scrolling text
        print("Displaying scrolling text in red...")
        controller.display_text("Welcome to RGB Matrix!", color=(255, 0, 0), scroll=True)
        time.sleep(10)
        
        # Display different colors
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
        ]
        
        for i, color in enumerate(colors):
            print(f"Displaying color {i+1}/6: RGB{color}")
            controller.display_text(f"Color {i+1}", color=color)
            time.sleep(2)
        
        # Clear the display
        print("Clearing display...")
        controller.clear()
        
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        controller.stop()
        print("Example completed!")


if __name__ == "__main__":
    main()
