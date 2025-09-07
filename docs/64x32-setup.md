# 64x32 RGB Matrix Setup Guide

## Your Matrix Specifications

**Matrix Size**: 64×32 pixels (64 columns, 32 rows)
**Total Pixels**: 2,048 pixels
**Aspect Ratio**: 2:1 (wide format)

## Optimal Configuration

### Power Requirements
- **Maximum Current**: ~4A (all pixels at full white)
- **Typical Usage**: ~1.5A (normal text/graphics)
- **Recommended Supply**: 5V 5A power adapter
- **Power Connector**: Usually barrel jack or screw terminals

### Display Characteristics
- **Text Capacity**: ~10 characters per line (with 6x10 font)
- **Visible Lines**: 2-3 lines of text (depending on font size)
- **Refresh Rate**: 60Hz+ (smooth display)
- **Color Depth**: 24-bit RGB (16.7M colors)

## Configuration Settings

Your project is already configured for 64x32! Key settings:

```yaml
matrix:
  rows: 32              # ✅ Correct for your matrix
  cols: 64              # ✅ Correct for your matrix
  brightness: 60        # Optimized for 64x32
  hardware_mapping: "adafruit-hat"
```

## Font Recommendations

### Best Fonts for 64x32:
1. **6x10.bdf** (default) - Good balance, ~10 chars/line
2. **4x6.bdf** - Smaller, more text, ~16 chars/line  
3. **8x13.bdf** - Larger, emphasis text, ~8 chars/line

### Text Positioning:
- **Single line**: Y position 10-16 (vertically centered)
- **Two lines**: Y positions 8 and 20
- **X position**: Start at 1-2 for left alignment

## Ideal Use Cases

### Perfect Applications:
- ✅ **Digital Clock** - Time fits perfectly
- ✅ **Weather Display** - Temp + condition
- ✅ **Stock Ticker** - Scrolling prices
- ✅ **News Headlines** - Scrolling text
- ✅ **System Status** - CPU, memory, etc.
- ✅ **Simple Games** - Pong, Snake, Tetris

### Content Guidelines:
- **Static Text**: Keep to 10 characters or less
- **Scrolling Text**: Any length works well
- **Graphics**: 64×32 pixel images/animations
- **Multiple Lines**: 2-3 lines max for readability

## Hardware Connections

### Using Adafruit RGB Matrix HAT (Recommended):
1. **Matrix to HAT**: 16-pin ribbon cable
2. **HAT to Pi**: Connects to 40-pin GPIO header
3. **Power**: 5V supply to matrix power input
4. **Ground**: Shared between Pi and matrix

### Power Supply Sizing:
- **Minimum**: 5V 3A (basic usage)
- **Recommended**: 5V 5A (full brightness/features)
- **Maximum**: 5V 6A (future expansion)

## Performance Optimization

### For Best Results:
```yaml
# In config.yaml
matrix:
  gpio_slowdown: 1      # Start with 1, increase if flickering
  pwm_bits: 11          # Good color depth
  brightness: 60        # Good visibility without overheating
  
performance:
  refresh_rate: 60      # Smooth display
  update_frequency: 30  # Responsive updates
```

### Troubleshooting 64x32 Issues:

**Flickering Display:**
- Increase `gpio_slowdown` to 2 or 3
- Check power supply capacity
- Ensure good ribbon cable connection

**Dim Display:**
- Increase brightness (max 100)
- Check power supply voltage (should be 5V)
- Verify power supply current rating

**Wrong Colors:**
- Check ribbon cable orientation
- Verify matrix type in config
- Test with known good image

**Text Too Small/Large:**
- Use different font sizes (4x6, 6x10, 8x13)
- Adjust text positioning
- Consider scrolling for longer text

## Example Commands

### Test Your 64x32 Matrix:
```bash
# Basic test
python examples/hello_world.py

# 64x32 specific demo
python examples/demo_64x32.py

# Digital clock (perfect for 64x32)
python examples/digital_clock.py

# Setup verification
python examples/test_setup.py
```

### Quick Configuration Check:
```bash
# Verify your config
cat config/config.yaml | grep -A 5 "matrix:"

# Should show:
# rows: 32
# cols: 64
```

## Sample Display Layouts

### Clock Layout:
```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                         12:34:56                               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Weather Layout:
```
┌────────────────────────────────────────────────────────────────┐
│  72°F                                                          │
│  Sunny                                                         │
└────────────────────────────────────────────────────────────────┘
```

### Scrolling Text:
```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│    ← This is scrolling text moving left                       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Test Hardware**: Run `python examples/demo_64x32.py`
2. **Customize Config**: Edit `config/config.yaml` as needed
3. **Create Content**: Build your own displays
4. **Web Interface**: Use `python src/web/app.py` for remote control

Your 64x32 matrix is perfectly configured and ready to use! 🚀
