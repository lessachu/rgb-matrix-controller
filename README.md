# RGB Matrix Controller

A comprehensive Python project for controlling Adafruit RGB LED matrices with Raspberry Pi.

**🎯 Featured: SFELC 2025 AI Hackathon Display!**

![RGB Matrix Demo](https://img.shields.io/badge/Matrix-64x32-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Compatible-red) ![Emulator](https://img.shields.io/badge/Emulator-Supported-orange)

## 🚀 SFELC 2025 AI Hackathon Demo

This project features a special display for the **SFELC 2025 AI Hackathon**:

```bash
# Run the hackathon display
python examples/sfelc_hackathon_pixel_display.py
```

**Features:**
- �� **"Hello SFELC 2025 AI Hackathon!"** scrolling message
- 🌈 **8 vibrant colors** cycling automatically
- 📱 **Browser-based emulator** at http://localhost:8888/
- ⚡ **Smooth pixel-perfect animation**
- 🎯 **Optimized for 64x32 matrices**

## 🎯 Features

- **Text Display**: Scrolling text, static messages, custom fonts
- **Graphics**: Images, animations, pixel art
- **Real-time Data**: Weather, time, system stats
- **Interactive Content**: Games, user input
- **Web Interface**: Control via browser
- **Configuration**: Easy setup and customization
- **Emulator Support**: Visual development without hardware

## 🛠️ Hardware Requirements

### RGB Matrix
- Adafruit RGB Matrix (64x32 recommended)
- RGB Matrix HAT or Bonnet for Raspberry Pi
- 5V Power Supply (5A recommended for 64x32)

### Raspberry Pi
- Raspberry Pi 3B+ or newer (Pi 4 recommended)
- MicroSD card (16GB+ recommended)

## 🚀 Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/lessachu/rgb-matrix-controller.git
cd rgb-matrix-controller

# Install dependencies (on Raspberry Pi)
./scripts/install.sh

# Or install emulator for development
pip install RGBMatrixEmulator pygame
```

### 2. Run Demos

```bash
# SFELC 2025 AI Hackathon display
python examples/sfelc_hackathon_pixel_display.py

# Basic emulator demo
python examples/simple_emulator_demo.py

# Test setup
python examples/test_setup.py
```

### 3. Configuration
```bash
# Edit for your matrix setup
cp config/config.example.yaml config/config.yaml
nano config/config.yaml
```

## 🎮 Emulator Support

This project includes full emulator support for development without hardware:

- **Visual Display**: Browser-based matrix at http://localhost:8888/
- **Real-time Updates**: See changes instantly
- **64x32 Simulation**: Exact hardware representation
- **Cross-platform**: Works on Mac, Windows, Linux

## 📁 Project Structure

```
rgb-matrix-controller/
├── src/                    # Main source code
│   ├── matrix/            # Matrix control modules
│   ├── displays/          # Different display types
│   ├── utils/             # Utility functions
│   └── web/               # Web interface
├── examples/              # Example scripts
│   ├── sfelc_hackathon_pixel_display.py  # 🎯 Hackathon demo
│   ├── simple_emulator_demo.py           # Basic emulator
│   └── hello_world.py                    # Getting started
├── config/                # Configuration files
├── assets/                # Images, fonts, data
├── scripts/               # Setup and utility scripts
├── tests/                 # Unit tests
└── docs/                  # Documentation
```

## 🎨 Example Usage

### Basic Text Display
```python
from src.matrix.emulator_controller import EmulatorController

controller = EmulatorController()
controller.display_text("Hello World!", color=(255, 0, 0))
```

### Scrolling Message
```python
controller.display_text("Your message here", scroll=True, color=(0, 255, 0))
```

### Digital Clock
```python
controller.start_clock(format="24h")
```

## 🌐 Web Interface
```bash
python src/web/app.py
# Open browser to http://raspberry-pi-ip:5000
```

## 📚 Documentation

- [Hardware Setup Guide](docs/hardware-setup.md)
- [64x32 Matrix Setup](docs/64x32-setup.md)
- [API Reference](docs/api-reference.md)
- [Examples & Tutorials](docs/examples.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Adafruit RGB Matrix Library](https://github.com/adafruit/Adafruit_CircuitPython_RGB_Display)
- [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)
- [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator)
- Raspberry Pi Foundation

---

**🎉 Ready for SFELC 2025 AI Hackathon!** 🌈✨
