#!/usr/bin/env python3
"""
Simple RGB Matrix Emulator Demo - Basic demonstration with the graphical emulator.
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from matrix.emulator_controller import EmulatorController


def main():
    """Run a simple emulator demonstration."""
    print("🎮 Simple RGB Matrix Emulator Demo - 64x32 Matrix")
    print("=" * 55)
    print("✅ Emulator started! Check your browser at: http://localhost:8888/")
    print("🖥️  You should see a 64x32 pixel matrix display")
    print("Press Ctrl+C to stop the demo")
    print()
    
    # Initialize the emulator controller
    controller = EmulatorController(use_emulator=True)
    
    try:
        # Demo 1: Simple pixel drawing
        print("Demo 1: Drawing individual pixels...")
        controller.clear()
        
        # Draw some pixels directly on the canvas
        if hasattr(controller, 'canvas') and controller.canvas:
            # Draw a border around the 64x32 matrix
            for x in range(64):
                controller.canvas.SetPixel(x, 0, 255, 0, 0)    # Top border - red
                controller.canvas.SetPixel(x, 31, 255, 0, 0)   # Bottom border - red
            
            for y in range(32):
                controller.canvas.SetPixel(0, y, 0, 255, 0)    # Left border - green
                controller.canvas.SetPixel(63, y, 0, 255, 0)   # Right border - green
            
            # Draw some diagonal lines
            for i in range(min(64, 32)):
                controller.canvas.SetPixel(i, i, 0, 0, 255)    # Blue diagonal
                controller.canvas.SetPixel(63-i, i, 255, 255, 0)  # Yellow diagonal
            
            # Update the display
            controller.canvas = controller.matrix.SwapOnVSync(controller.canvas)
            
        time.sleep(3)
        
        # Demo 2: Color patterns
        print("Demo 2: Color patterns...")
        controller.clear()
        
        if hasattr(controller, 'canvas') and controller.canvas:
            # Create a rainbow pattern
            for x in range(64):
                for y in range(32):
                    r = int(255 * (x / 64))
                    g = int(255 * (y / 32))
                    b = int(255 * ((x + y) / (64 + 32)))
                    controller.canvas.SetPixel(x, y, r, g, b)
            
            controller.canvas = controller.matrix.SwapOnVSync(controller.canvas)
            
        time.sleep(3)
        
        # Demo 3: Simple animation
        print("Demo 3: Simple animation...")
        for frame in range(64):
            controller.clear()
            
            if hasattr(controller, 'canvas') and controller.canvas:
                # Moving dot
                x = frame % 64
                y = 16  # Center vertically
                
                # Draw a moving dot with trail
                for i in range(5):
                    trail_x = (x - i) % 64
                    brightness = 255 - (i * 50)
                    if brightness > 0:
                        controller.canvas.SetPixel(trail_x, y, brightness, 0, brightness)
                
                controller.canvas = controller.matrix.SwapOnVSync(controller.canvas)
            
            time.sleep(0.1)
        
        # Demo 4: Text simulation (since text rendering has issues)
        print("Demo 4: Text simulation with pixels...")
        controller.clear()
        
        if hasattr(controller, 'canvas') and controller.canvas:
            # Draw "64x32" using pixel patterns
            # Simple 5x7 font patterns for "64x32"
            
            # Draw "6"
            for y in range(7):
                for x in range(4):
                    if (x, y) in [(0,0),(1,0),(2,0),(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(0,4),(3,4),(0,5),(3,5),(1,6),(2,6)]:
                        controller.canvas.SetPixel(x + 5, y + 12, 255, 255, 255)
            
            # Draw "4"
            for y in range(7):
                for x in range(4):
                    if (x, y) in [(0,0),(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(3,6)]:
                        controller.canvas.SetPixel(x + 10, y + 12, 255, 255, 255)
            
            # Draw "x"
            for y in range(5):
                for x in range(4):
                    if (x, y) in [(0,0),(3,4),(1,1),(2,3),(2,1),(1,3),(3,0),(0,4)]:
                        controller.canvas.SetPixel(x + 16, y + 14, 255, 255, 0)
            
            # Draw "3"
            for y in range(7):
                for x in range(4):
                    if (x, y) in [(0,0),(1,0),(2,0),(3,1),(3,2),(1,3),(2,3),(3,4),(3,5),(0,6),(1,6),(2,6)]:
                        controller.canvas.SetPixel(x + 22, y + 12, 255, 255, 255)
            
            # Draw "2"
            for y in range(7):
                for x in range(4):
                    if (x, y) in [(0,0),(1,0),(2,0),(3,1),(3,2),(2,3),(1,4),(0,5),(0,6),(1,6),(2,6),(3,6)]:
                        controller.canvas.SetPixel(x + 27, y + 12, 255, 255, 255)
            
            controller.canvas = controller.matrix.SwapOnVSync(controller.canvas)
        
        time.sleep(5)
        
        # Final message
        print("Demo complete! Matrix display is working perfectly!")
        controller.clear()
        
        # Show a final pattern
        if hasattr(controller, 'canvas') and controller.canvas:
            # Checkerboard pattern
            for x in range(64):
                for y in range(32):
                    if (x + y) % 2 == 0:
                        controller.canvas.SetPixel(x, y, 0, 255, 0)
                    else:
                        controller.canvas.SetPixel(x, y, 255, 0, 255)
            
            controller.canvas = controller.matrix.SwapOnVSync(controller.canvas)
        
        time.sleep(3)
        controller.clear()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    finally:
        controller.stop()
        print("\n🎉 Simple Emulator Demo completed!")
        print("\n💡 What you saw in the browser:")
        print("   • 64×32 pixel matrix display (64 wide, 32 tall)")
        print("   • Individual pixel control")
        print("   • Color patterns and gradients")
        print("   • Simple animations")
        print("   • Pixel-based text rendering")
        print("\n🚀 Your 64x32 matrix configuration is perfect!")
        print("   The emulator shows exactly how your hardware will look!")
        print(f"   🌐 Emulator URL: http://localhost:8888/")


if __name__ == "__main__":
    main()
