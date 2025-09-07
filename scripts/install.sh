#!/bin/bash
# RGB Matrix Controller Installation Script

echo "🌈 RGB Matrix Controller Installation"
echo "====================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    echo "   You can still install for development/testing purposes"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    python3-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libopenjp2-7 \
    libtiff5 \
    libatlas-base-dev \
    libopenblas-dev

# Install RGB matrix library dependencies
echo "🎨 Installing RGB matrix library dependencies..."
sudo apt install -y \
    libgraphicsmagick++-dev \
    libwebp-dev \
    librgbmatrix-dev

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install RGB matrix library from source (if not available via pip)
echo "🔗 Installing RGB matrix library..."
if ! pip show rpi-rgb-led-matrix > /dev/null 2>&1; then
    echo "Installing from source..."
    cd /tmp
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
    cd rpi-rgb-led-matrix
    make build-python PYTHON=$(which python3)
    sudo make install-python PYTHON=$(which python3)
    cd -
fi

# Create default config
echo "⚙️  Setting up configuration..."
if [ ! -f config/config.yaml ]; then
    cp config/config.example.yaml config/config.yaml
    echo "✅ Created config/config.yaml from example"
fi

# Set up systemd service (optional)
read -p "🔄 Install as system service? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Setting up systemd service..."
    sudo cp scripts/rgb-matrix.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "✅ Service installed. Use 'sudo systemctl start rgb-matrix' to start"
fi

# Make scripts executable
chmod +x scripts/*.sh
chmod +x examples/*.py

echo ""
echo "🎉 Installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit config/config.yaml for your matrix setup"
echo "2. Test with: python examples/hello_world.py"
echo "3. Check docs/ for more information"
echo ""
echo "💡 Remember to run with sudo on Raspberry Pi for GPIO access"
