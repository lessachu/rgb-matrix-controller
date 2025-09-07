#!/usr/bin/env python3
"""
Digital Clock Example - Real-time clock display on RGB matrix.
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from matrix.controller import MatrixController


def main():
    """Run the digital clock example."""
    print("🕐 RGB Matrix Digital Clock")
    print("=" * 30)
    print("Press Ctrl+C to stop")
    
    # Initialize the matrix controller
    controller = MatrixController()
    
    try:
        # Start the clock (24-hour format)
        print("Starting 24-hour clock display...")
        controller.start_clock(format="24h")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping clock...")
    finally:
        controller.stop()
        controller.clear()
        print("Clock stopped!")


if __name__ == "__main__":
    main()
