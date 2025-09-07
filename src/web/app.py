#!/usr/bin/env python3
"""
RGB Matrix Web Interface - Flask web app for controlling the matrix remotely.
"""

import sys
import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from matrix.controller import MatrixController

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rgb-matrix-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global matrix controller
matrix_controller = None

def get_controller():
    """Get or create matrix controller instance."""
    global matrix_controller
    if matrix_controller is None:
        matrix_controller = MatrixController()
    return matrix_controller

@app.route('/')
def index():
    """Main web interface page."""
    return render_template('index.html')

@app.route('/api/display/text', methods=['POST'])
def display_text():
    """API endpoint to display text."""
    try:
        data = request.get_json()
        text = data.get('text', 'Hello World!')
        color = data.get('color', [255, 255, 255])
        scroll = data.get('scroll', False)
        
        controller = get_controller()
        controller.display_text(text, tuple(color), scroll)
        
        return jsonify({'status': 'success', 'message': f'Displaying: {text}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/display/clear', methods=['POST'])
def clear_display():
    """API endpoint to clear the display."""
    try:
        controller = get_controller()
        controller.clear()
        return jsonify({'status': 'success', 'message': 'Display cleared'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/clock/start', methods=['POST'])
def start_clock():
    """API endpoint to start the clock."""
    try:
        data = request.get_json()
        format_type = data.get('format', '24h')
        
        controller = get_controller()
        controller.start_clock(format_type)
        
        return jsonify({'status': 'success', 'message': f'Clock started ({format_type})'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/brightness', methods=['POST'])
def set_brightness():
    """API endpoint to set brightness."""
    try:
        data = request.get_json()
        brightness = data.get('brightness', 50)
        
        controller = get_controller()
        controller.set_brightness(brightness)
        
        return jsonify({'status': 'success', 'message': f'Brightness set to {brightness}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('status', {'message': 'Connected to RGB Matrix Controller'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

if __name__ == '__main__':
    print("🌐 Starting RGB Matrix Web Interface...")
    print("📱 Open your browser to http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
