# Hardware Setup Guide

## Required Components

### 1. RGB LED Matrix
- **Adafruit RGB Matrix Panel** (32x32, 64x32, or 64x64 pixels)
- **Voltage**: 5V DC
- **Current**: Varies by size (check specifications)

### 2. Raspberry Pi
- **Model**: Pi 3B+ or newer (Pi 4 recommended)
- **OS**: Raspberry Pi OS (32-bit or 64-bit)
- **Storage**: 16GB+ microSD card

### 3. RGB Matrix HAT/Bonnet
- **Adafruit RGB Matrix HAT** (for Pi with 40-pin header)
- **Adafruit RGB Matrix Bonnet** (for Pi Zero)

### 4. Power Supply
- **5V DC power supply** with adequate amperage
- **Current requirements**:
  - 32x32 matrix: ~4A
  - 64x32 matrix: ~6A
  - 64x64 matrix: ~8A

## Wiring Connections

### Using RGB Matrix HAT/Bonnet (Recommended)
1. Connect HAT/Bonnet to Raspberry Pi GPIO header
2. Connect matrix ribbon cable to HAT/Bonnet
3. Connect power supply to matrix power input
4. Connect power supply to HAT/Bonnet (if required)

### Manual GPIO Wiring (Advanced)
If not using HAT/Bonnet, connect matrix pins to Pi GPIO:

```
Matrix Pin  | Pi GPIO | Description
------------|---------|-------------
R1          | GPIO 11 | Red data (top half)
G1          | GPIO 12 | Green data (top half)
B1          | GPIO 13 | Blue data (top half)
R2          | GPIO 15 | Red data (bottom half)
G2          | GPIO 16 | Green data (bottom half)
B2          | GPIO 18 | Blue data (bottom half)
A           | GPIO 7  | Row select A
B           | GPIO 8  | Row select B
C           | GPIO 9  | Row select C
D           | GPIO 10 | Row select D (32+ row matrices)
CLK         | GPIO 23 | Clock
LAT         | GPIO 24 | Latch
OE          | GPIO 25 | Output Enable
GND         | GND     | Ground
```

## Power Considerations

### Important Safety Notes
- **Never power matrix from Pi**: The Pi cannot provide enough current
- **Use dedicated 5V supply**: Match the current requirements
- **Common ground**: Ensure Pi and matrix share common ground
- **Proper gauge wire**: Use appropriate wire gauge for current

### Power Supply Sizing
Calculate power requirements:
- **Per pixel**: ~60mA at full white
- **32x32 matrix**: 1024 pixels × 60mA = ~61A (theoretical max)
- **Typical usage**: 20-30% of max (12-18A for 32x32)

## Assembly Steps

### 1. Prepare Raspberry Pi
1. Flash Raspberry Pi OS to microSD card
2. Enable SSH (optional)
3. Boot and complete initial setup

### 2. Install HAT/Bonnet
1. Power off Raspberry Pi
2. Carefully align HAT/Bonnet with GPIO header
3. Press down firmly to ensure good connection
4. Secure with standoffs if provided

### 3. Connect Matrix
1. Connect ribbon cable from matrix to HAT/Bonnet
2. Ensure proper orientation (check pin 1 marking)
3. Press connector firmly into place

### 4. Connect Power
1. Connect 5V power supply to matrix power input
2. If using HAT with power input, connect there too
3. **Do not power on yet**

### 5. Software Setup
1. Install RGB matrix software (see installation guide)
2. Configure matrix parameters
3. Test with simple example

## Testing

### Basic Connectivity Test
```bash
# Test GPIO access
sudo python3 -c "import RPi.GPIO; print('GPIO OK')"

# Test matrix library
python3 examples/hello_world.py
```

### Troubleshooting Common Issues

**Matrix not lighting up:**
- Check power supply connections
- Verify ribbon cable orientation
- Ensure adequate power supply current

**Flickering or dim display:**
- Insufficient power supply
- Poor connections
- GPIO timing issues (try gpio_slowdown setting)

**Colors incorrect:**
- Check RGB pin connections
- Verify matrix type in configuration
- Test with known good image

**Permission errors:**
- Run with sudo for GPIO access
- Check user groups (gpio, spi)

## Safety Warnings

⚠️ **Important Safety Notes:**
- Always power off before making connections
- Use proper current-rated power supplies
- Ensure good ventilation for power supplies
- Check connections before powering on
- Never exceed matrix voltage ratings

## Next Steps

Once hardware is set up:
1. [Software Installation](installation.md)
2. [Configuration Guide](configuration.md)
3. [Running Examples](examples.md)
