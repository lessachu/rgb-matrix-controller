#!/usr/bin/env python3
"""
RGB Matrix Controller - Main controller class for managing RGB LED matrix displays.
"""

import time
import threading
from typing import Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
import yaml
import os

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
    MATRIX_AVAILABLE = True
except ImportError:
    print("Warning: rgbmatrix library not found. Running in simulation mode.")
    MATRIX_AVAILABLE = False


class MatrixController:
    """Main controller for RGB LED matrix operations."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the matrix controller."""
        self.config = self._load_config(config_path)
        self.matrix = None
        self.canvas = None
        self.running = False
        self._current_thread = None
        
        if MATRIX_AVAILABLE:
            self._setup_matrix()
        else:
            print("Running in simulation mode - matrix operations will be logged only")
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using defaults.")
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            'matrix': {
                'rows': 32,
                'cols': 64,
                'chain_length': 1,
                'parallel': 1,
                'brightness': 50,
                'hardware_mapping': 'adafruit-hat'
            },
            'display': {
                'default_font': 'assets/fonts/6x10.bdf',
                'scroll_speed': 0.05
            }
        }
    
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
        if MATRIX_AVAILABLE and self.canvas:
            self.canvas.Clear()
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
        else:
            print("SIMULATION: Matrix cleared")
    
    def display_text(self, text: str, color: Tuple[int, int, int] = (255, 255, 255), 
                    scroll: bool = False, font_path: Optional[str] = None):
        """Display text on the matrix."""
        if not MATRIX_AVAILABLE:
            print(f"SIMULATION: Display text '{text}' in color {color}, scroll={scroll}")
            return
        
        if scroll:
            self._scroll_text(text, color, font_path)
        else:
            self._static_text(text, color, font_path)
    
    def _static_text(self, text: str, color: Tuple[int, int, int], font_path: Optional[str]):
        """Display static text."""
        self.canvas.Clear()
        
        if font_path and os.path.exists(font_path):
            font = graphics.Font()
            font.LoadFont(font_path)
        else:
            font = graphics.Font()
            font.LoadFont("assets/fonts/6x10.bdf")  # Default font
        
        text_color = graphics.Color(color[0], color[1], color[2])
        graphics.DrawText(self.canvas, font, 2, 10, text_color, text)
        
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
    
    def _scroll_text(self, text: str, color: Tuple[int, int, int], font_path: Optional[str]):
        """Scroll text across the matrix."""
        self.running = True
        
        def scroll_worker():
            font = graphics.Font()
            if font_path and os.path.exists(font_path):
                font.LoadFont(font_path)
            else:
                font.LoadFont("assets/fonts/6x10.bdf")
            
            text_color = graphics.Color(color[0], color[1], color[2])
            pos = self.matrix.width
            
            while self.running:
                self.canvas.Clear()
                length = graphics.DrawText(self.canvas, font, pos, 10, text_color, text)
                pos -= 1
                if pos + length < 0:
                    pos = self.matrix.width
                
                time.sleep(self.config['display']['scroll_speed'])
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
        
        if self._current_thread and self._current_thread.is_alive():
            self.stop()
        
        self._current_thread = threading.Thread(target=scroll_worker)
        self._current_thread.start()
    
    def display_image(self, image_path: str):
        """Display an image on the matrix."""
        if not MATRIX_AVAILABLE:
            print(f"SIMULATION: Display image '{image_path}'")
            return
        
        try:
            image = Image.open(image_path)
            image = image.resize((self.matrix.width, self.matrix.height), Image.LANCZOS)
            image = image.convert('RGB')
            
            self.canvas.Clear()
            for y in range(self.matrix.height):
                for x in range(self.matrix.width):
                    r, g, b = image.getpixel((x, y))
                    self.canvas.SetPixel(x, y, r, g, b)
            
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
        except Exception as e:
            print(f"Error displaying image: {e}")
    
    def start_clock(self, format: str = "24h"):
        """Start a real-time clock display."""
        self.running = True
        
        def clock_worker():
            while self.running:
                current_time = time.strftime("%H:%M:%S" if format == "24h" else "%I:%M:%S %p")
                if MATRIX_AVAILABLE:
                    self._static_text(current_time, (0, 255, 0), None)
                else:
                    print(f"SIMULATION: Clock display - {current_time}")
                time.sleep(1)
        
        if self._current_thread and self._current_thread.is_alive():
            self.stop()
        
        self._current_thread = threading.Thread(target=clock_worker)
        self._current_thread.start()
    
    def stop(self):
        """Stop any running display operations."""
        self.running = False
        if self._current_thread and self._current_thread.is_alive():
            self._current_thread.join(timeout=2)
    
    def set_brightness(self, brightness: int):
        """Set matrix brightness (0-100)."""
        if MATRIX_AVAILABLE and self.matrix:
            self.matrix.brightness = max(0, min(100, brightness))
        else:
            print(f"SIMULATION: Set brightness to {brightness}")
    
    def __del__(self):
        """Cleanup when controller is destroyed."""
        self.stop()
        if MATRIX_AVAILABLE and self.matrix:
            self.clear()
