# RGB Matrix Controller

A comprehensive Python project for controlling Adafruit RGB LED matrices with Raspberry Pi.

## 🎯 Features

- **Text Display**: Scrolling text, static messages, custom fonts
- **Graphics**: Images, animations, pixel art
- **Real-time Data**: Weather, time, system stats
- **Interactive Content**: Games, user input
- **Web Interface**: Control via browser
- **Configuration**: Easy setup and customization

## 🛠️ Hardware Requirements

### RGB Matrix
- Adafruit RGB Matrix (32x32, 64x32, 64x64, etc.)
- RGB Matrix HAT or Bonnet for Raspberry Pi
- 5V Power Supply (adequate amperage for your matrix size)

### Raspberry Pi
- Raspberry Pi 3B+ or newer (Pi 4 recommended)
- MicroSD card (16GB+ recommended)
- HDMI cable (for initial setup)

## 🚀 Quick Start

### 1. Hardware Setup
1. Connect RGB Matrix to HAT/Bonnet
2. Connect HAT/Bonnet to Raspberry Pi GPIO pins
3. Connect power supply to matrix
4. Boot Raspberry Pi

### 2. Software Installation
```bash
# Clone this repository
git clone <your-repo-url>
cd rgb-matrix-controller

# Install dependencies
./scripts/install.sh

# Run basic test
python examples/hello_world.py
```

## 📁 Project Structure

```
rgb-matrix-controller/
├── src/                    # Main source code
│   ├── matrix/            # Matrix control modules
│   ├── displays/          # Different display types
│   ├── utils/             # Utility functions
│   └── web/               # Web interface
├── examples/              # Example scripts
├── config/                # Configuration files
├── assets/                # Images, fonts, data
├── scripts/               # Setup and utility scripts
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── requirements.txt       # Python dependencies
```

## 🎮 Usage Examples

### Basic Text Display
```python
from src.matrix.controller import MatrixController

controller = MatrixController()
controller.display_text("Hello World!", scroll=True)
```

### Show Image
```python
controller.display_image("assets/images/logo.png")
```

### Real-time Clock
```python
controller.start_clock(format="12h")
```

### Web Interface
```bash
python src/web/app.py
# Open browser to http://raspberry-pi-ip:5000
```

## 📚 Documentation

- [Hardware Setup Guide](docs/hardware-setup.md)
- [Software Installation](docs/installation.md)
- [API Reference](docs/api-reference.md)
- [Examples & Tutorials](docs/examples.md)
- [Troubleshooting](docs/troubleshooting.md)

---

**Happy LED Matrix Hacking!** 🌈✨
