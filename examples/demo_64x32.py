#!/usr/bin/env python3
"""
64x32 Matrix Demo - Showcase features optimized for 64x32 RGB matrix.
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from matrix.controller import MatrixController


def main():
    """Run the 64x32 matrix demonstration."""
    print("🌈 64x32 RGB Matrix Demonstration")
    print("=" * 40)
    print("Matrix size: 64 columns × 32 rows")
    print("Optimized for your specific hardware!")
    print()
    
    # Initialize the matrix controller
    controller = MatrixController()
    
    try:
        # Demo 1: Text positioning for 64x32
        print("Demo 1: Text positioning optimized for 64x32...")
        controller.display_text("64x32", color=(255, 0, 0))
        time.sleep(2)
        
        controller.display_text("MATRIX", color=(0, 255, 0))
        time.sleep(2)
        
        controller.display_text("DEMO", color=(0, 0, 255))
        time.sleep(2)
        
        # Demo 2: Scrolling text that fits 64x32 well
        print("Demo 2: Scrolling text optimized for 64 pixel width...")
        messages = [
            "Welcome to your 64x32 RGB Matrix!",
            "Perfect size for text and graphics",
            "64 pixels wide, 32 pixels tall",
            "Great for clocks, weather, news!"
        ]
        
        for message in messages:
            print(f"  Scrolling: {message}")
            controller.display_text(message, color=(255, 255, 0), scroll=True)
            time.sleep(8)  # Let it scroll a few times
        
        # Demo 3: Color showcase
        print("Demo 3: Color showcase...")
        colors = [
            ((255, 0, 0), "RED"),
            ((0, 255, 0), "GREEN"), 
            ((0, 0, 255), "BLUE"),
            ((255, 255, 0), "YELLOW"),
            ((255, 0, 255), "MAGENTA"),
            ((0, 255, 255), "CYAN"),
            ((255, 128, 0), "ORANGE"),
            ((128, 0, 255), "PURPLE"),
        ]
        
        for color, name in colors:
            print(f"  Displaying: {name}")
            controller.display_text(name, color=color)
            time.sleep(1.5)
        
        # Demo 4: Clock display (great for 64x32)
        print("Demo 4: Digital clock (perfect for 64x32)...")
        print("  Running clock for 10 seconds...")
        controller.start_clock(format="24h")
        time.sleep(10)
        
        # Demo 5: Brightness levels
        print("Demo 5: Brightness demonstration...")
        brightness_levels = [25, 50, 75, 100, 75, 50, 25]
        
        controller.display_text("BRIGHT", color=(255, 255, 255))
        
        for brightness in brightness_levels:
            print(f"  Setting brightness to {brightness}%")
            controller.set_brightness(brightness)
            time.sleep(1)
        
        # Demo 6: Rapid text changes (good for 64x32)
        print("Demo 6: Rapid text updates...")
        words = ["FAST", "TEXT", "UPDATES", "ON", "64x32", "MATRIX"]
        
        for word in words:
            controller.display_text(word, color=(0, 255, 255))
            time.sleep(0.8)
        
        # Final message
        print("Demo complete! Showing final message...")
        controller.display_text("64x32 READY!", color=(0, 255, 0), scroll=True)
        time.sleep(5)
        
        # Clear the display
        print("Clearing display...")
        controller.clear()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    finally:
        controller.stop()
        print("\n🎉 64x32 Matrix Demo completed!")
        print("\n💡 Your matrix is configured and ready!")
        print("   • Matrix size: 64×32 pixels")
        print("   • Optimal text: ~10 characters per line")
        print("   • Perfect for: clocks, weather, short messages")
        print("   • Power needs: ~4A max, ~1.5A typical")


if __name__ == "__main__":
    main()
