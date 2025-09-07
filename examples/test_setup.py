#!/usr/bin/env python3
"""
Setup Test - Verify that the RGB matrix controller setup is working.
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all required modules can be imported."""
    print("�� Testing imports...")
    
    try:
        from matrix.controller import MatrixController
        print("✅ MatrixController import successful")
    except ImportError as e:
        print(f"❌ MatrixController import failed: {e}")
        return False
    
    try:
        import yaml
        print("✅ YAML import successful")
    except ImportError as e:
        print(f"❌ YAML import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL import successful")
    except ImportError as e:
        print(f"❌ PIL import failed: {e}")
        return False
    
    return True

def test_controller():
    """Test basic controller functionality."""
    print("\n🎮 Testing controller...")
    
    try:
        from matrix.controller import MatrixController
        controller = MatrixController()
        print("✅ Controller initialization successful")
        
        # Test basic operations (in simulation mode)
        controller.display_text("Test", color=(255, 0, 0))
        print("✅ Text display test successful")
        
        controller.clear()
        print("✅ Clear display test successful")
        
        controller.set_brightness(75)
        print("✅ Brightness control test successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Controller test failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n⚙️  Testing configuration...")
    
    config_path = "config/config.example.yaml"
    if os.path.exists(config_path):
        print(f"✅ Example config found: {config_path}")
        
        try:
            import yaml
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            print("✅ Config parsing successful")
            
            # Check required sections
            required_sections = ['matrix', 'display']
            for section in required_sections:
                if section in config:
                    print(f"✅ Config section '{section}' found")
                else:
                    print(f"❌ Config section '{section}' missing")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Config parsing failed: {e}")
            return False
    else:
        print(f"❌ Example config not found: {config_path}")
        return False

def main():
    """Run all setup tests."""
    print("🌈 RGB Matrix Controller Setup Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Controller Test", test_controller),
        ("Configuration Test", test_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is working correctly.")
        print("\n📋 Next steps:")
        print("1. Copy config/config.example.yaml to config/config.yaml")
        print("2. Edit config/config.yaml for your matrix setup")
        print("3. Run: python examples/hello_world.py")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n�� Common solutions:")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Check file paths and permissions")
        print("- Ensure you're in the project root directory")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
