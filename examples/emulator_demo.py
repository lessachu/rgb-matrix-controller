#!/usr/bin/env python3
"""
RGB Matrix Emulator Demo - Visual demonstration using the graphical emulator.
"""

import sys
import os
import time
import math

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from matrix.emulator_controller import EmulatorController


def main():
    """Run the emulator demonstration."""
    print("🎮 RGB Matrix Emulator Demo - 64x32 Matrix")
    print("=" * 50)
    print("This demo will open a graphical window showing your 64x32 matrix!")
    print("Press Ctrl+C to stop the demo")
    print()
    
    # Initialize the emulator controller
    controller = EmulatorController(use_emulator=True)
    
    try:
        # Demo 1: Welcome message
        print("Demo 1: Welcome message...")
        controller.display_text("64x32", color=(255, 0, 0), x=20, y=10)
        time.sleep(2)
        
        controller.display_text("MATRIX", color=(0, 255, 0), x=15, y=20)
        time.sleep(2)
        
        controller.clear()
        time.sleep(1)
        
        # Demo 2: Scrolling text
        print("Demo 2: Scrolling text...")
        controller.display_text("Welcome to your 64x32 RGB Matrix Emulator!", 
                               color=(255, 255, 0), scroll=True)
        time.sleep(8)
        
        controller.stop()
        controller.clear()
        time.sleep(1)
        
        # Demo 3: Color showcase
        print("Demo 3: Color showcase...")
        colors = [
            ((255, 0, 0), "RED"),
            ((0, 255, 0), "GREEN"), 
            ((0, 0, 255), "BLUE"),
            ((255, 255, 0), "YELLOW"),
            ((255, 0, 255), "MAGENTA"),
            ((0, 255, 255), "CYAN"),
        ]
        
        for color, name in colors:
            print(f"  Showing: {name}")
            controller.display_text(name, color=color, x=5, y=16)
            time.sleep(1.5)
        
        controller.clear()
        time.sleep(1)
        
        # Demo 4: Digital clock
        print("Demo 4: Digital clock (10 seconds)...")
        controller.clear()
        controller.start_clock(format="24h")
        time.sleep(10)
        
        # Demo 5: Brightness levels
        print("Demo 5: Brightness demonstration...")
        controller.stop()
        controller.display_text("BRIGHT", color=(255, 255, 255), x=10, y=16)
        
        brightness_levels = [25, 50, 75, 100, 75, 50, 25]
        for brightness in brightness_levels:
            print(f"  Setting brightness to {brightness}%")
            controller.set_brightness(brightness)
            time.sleep(1)
        
        # Final message
        print("Demo complete! Showing final message...")
        controller.clear()
        controller.display_text("DEMO DONE!", color=(0, 255, 0), x=5, y=16)
        time.sleep(3)
        
        controller.display_text("Your 64x32 matrix is ready!", 
                               color=(255, 255, 255), scroll=True)
        time.sleep(8)
        
        # Clear the display
        controller.clear()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    finally:
        controller.stop()
        print("\n🎉 Emulator Demo completed!")
        print("\n💡 What you saw:")
        print("   • 64×32 pixel matrix display")
        print("   • Text rendering and scrolling")
        print("   • Color display capabilities")
        print("   • Real-time clock")
        print("   • Brightness control")
        print("\n🚀 Your matrix configuration is perfect!")
        print("   Ready to deploy to Raspberry Pi hardware!")


if __name__ == "__main__":
    main()
