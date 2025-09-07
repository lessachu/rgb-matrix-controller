#!/usr/bin/env python3
"""
RGB Matrix Emulator Controller - Enhanced controller with graphical emulator support.
"""

import time
import threading
from typing import Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
import yaml
import os

# Try to import the emulator first, then fall back to hardware or simulation
EMULATOR_AVAILABLE = False
MATRIX_AVAILABLE = False

try:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    EMULATOR_AVAILABLE = True
    print("✅ RGB Matrix Emulator loaded - graphical display available!")
except ImportError:
    try:
        from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
        MATRIX_AVAILABLE = True
        print("✅ Hardware RGB Matrix library loaded")
    except ImportError:
        print("⚠️  No matrix library found. Running in text simulation mode.")


class EmulatorController:
    """Enhanced matrix controller with emulator support for development."""
    
    def __init__(self, config_path: str = "config/config.yaml", use_emulator: bool = True):
        """Initialize the matrix controller with emulator support."""
        self.config = self._load_config(config_path)
        self.matrix = None
        self.canvas = None
        self.running = False
        self._current_thread = None
        self.use_emulator = use_emulator and EMULATOR_AVAILABLE
        
        if self.use_emulator and EMULATOR_AVAILABLE:
            self._setup_emulator()
        elif MATRIX_AVAILABLE:
            self._setup_matrix()
        else:
            print("Running in text simulation mode - operations will be logged only")
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using defaults.")
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Return default configuration for 64x32 matrix."""
        return {
            'matrix': {
                'rows': 32,
                'cols': 64,
                'chain_length': 1,
                'parallel': 1,
                'brightness': 60,
                'hardware_mapping': 'adafruit-hat'
            },
            'display': {
                'default_font': 'assets/fonts/6x10.bdf',
                'scroll_speed': 0.05
            }
        }
    
    def _setup_emulator(self):
        """Initialize the RGB matrix emulator."""
        options = RGBMatrixOptions()
        options.rows = self.config['matrix']['rows']
        options.cols = self.config['matrix']['cols']
        options.chain_length = self.config['matrix']['chain_length']
        options.parallel = self.config['matrix']['parallel']
        options.brightness = self.config['matrix']['brightness']
        options.hardware_mapping = self.config['matrix'].get('hardware_mapping', 'adafruit-hat')
        
        self.matrix = RGBMatrix(options=options)
        self.canvas = self.matrix.CreateFrameCanvas()
        
        print(f"🎮 Emulator initialized: {options.cols}x{options.rows} matrix")
        print("   A graphical window should appear showing your matrix!")
    
    def _setup_matrix(self):
        """Initialize the RGB matrix hardware."""
        options = RGBMatrixOptions()
        options.rows = self.config['matrix']['rows']
        options.cols = self.config['matrix']['cols']
        options.chain_length = self.config['matrix']['chain_length']
        options.parallel = self.config['matrix']['parallel']
        options.brightness = self.config['matrix']['brightness']
        options.hardware_mapping = self.config['matrix'].get('hardware_mapping', 'adafruit-hat')
        
        self.matrix = RGBMatrix(options=options)
        self.canvas = self.matrix.CreateFrameCanvas()
    
    def clear(self):
        """Clear the matrix display."""
        if (EMULATOR_AVAILABLE or MATRIX_AVAILABLE) and self.canvas:
            self.canvas.Clear()
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
        else:
            print("SIMULATION: Matrix cleared")
    
    def display_text(self, text: str, color: Tuple[int, int, int] = (255, 255, 255), 
                    scroll: bool = False, font_path: Optional[str] = None, 
                    x: int = 1, y: int = 10):
        """Display text on the matrix."""
        if not (EMULATOR_AVAILABLE or MATRIX_AVAILABLE):
            print(f"SIMULATION: Display text '{text}' at ({x},{y}) in color {color}, scroll={scroll}")
            return
        
        if scroll:
            self._scroll_text(text, color, font_path, y)
        else:
            self._static_text(text, color, font_path, x, y)
    
    def _static_text(self, text: str, color: Tuple[int, int, int], 
                    font_path: Optional[str], x: int, y: int):
        """Display static text."""
        self.canvas.Clear()
        
        # Use built-in font for emulator
        font = graphics.Font()
        try:
            font.LoadFont("6x10.bdf")  # Built-in font
        except:
            pass  # Use default font
        
        text_color = graphics.Color(color[0], color[1], color[2])
        graphics.DrawText(self.canvas, font, x, y, text_color, text)
        
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
    
    def _scroll_text(self, text: str, color: Tuple[int, int, int], 
                    font_path: Optional[str], y: int):
        """Scroll text across the matrix."""
        self.running = True
        
        def scroll_worker():
            font = graphics.Font()
            try:
                font.LoadFont("6x10.bdf")  # Built-in font
            except:
                pass  # Use default font
            
            text_color = graphics.Color(color[0], color[1], color[2])
            pos = self.matrix.width
            
            while self.running:
                self.canvas.Clear()
                length = graphics.DrawText(self.canvas, font, pos, y, text_color, text)
                pos -= 1
                if pos + length < 0:
                    pos = self.matrix.width
                
                time.sleep(self.config['display']['scroll_speed'])
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
        
        if self._current_thread and self._current_thread.is_alive():
            self.stop()
        
        self._current_thread = threading.Thread(target=scroll_worker)
        self._current_thread.start()
    
    def start_clock(self, format: str = "24h"):
        """Start a real-time clock display."""
        self.running = True
        
        def clock_worker():
            while self.running:
                current_time = time.strftime("%H:%M:%S" if format == "24h" else "%I:%M:%S %p")
                if EMULATOR_AVAILABLE or MATRIX_AVAILABLE:
                    self._static_text(current_time, (0, 255, 0), None, 2, 16)
                else:
                    print(f"SIMULATION: Clock display - {current_time}")
                time.sleep(1)
        
        if self._current_thread and self._current_thread.is_alive():
            self.stop()
        
        self._current_thread = threading.Thread(target=clock_worker)
        self._current_thread.start()
    
    def set_brightness(self, brightness: int):
        """Set matrix brightness (0-100)."""
        if (EMULATOR_AVAILABLE or MATRIX_AVAILABLE) and self.matrix:
            self.matrix.brightness = max(0, min(100, brightness))
        else:
            print(f"SIMULATION: Set brightness to {brightness}")
    
    def stop(self):
        """Stop any running display operations."""
        self.running = False
        if self._current_thread and self._current_thread.is_alive():
            self._current_thread.join(timeout=2)
    
    def __del__(self):
        """Cleanup when controller is destroyed."""
        self.stop()
        if (EMULATOR_AVAILABLE or MATRIX_AVAILABLE) and self.matrix:
            self.clear()
