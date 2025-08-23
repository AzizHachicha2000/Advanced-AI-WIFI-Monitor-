#!/usr/bin/env python3
"""
Simple script to test if the ESP32 code compiles without errors
"""

import subprocess
import sys
import os

def test_compilation():
    """
    Test if the PlatformIO project compiles successfully
    """
    print("Testing ESP32 code compilation...")
    
    # Check if we're in the right directory
    if not os.path.exists('platformio.ini'):
        print("Error: platformio.ini not found. Make sure you're in the project directory.")
        return False
    
    # Try different PlatformIO command variations
    pio_commands = [
        ['pio', 'run', '--target', 'checkprogsize'],
        ['platformio', 'run', '--target', 'checkprogsize'],
        ['python', '-m', 'platformio', 'run', '--target', 'checkprogsize'],
        ['~/.platformio/penv/bin/platformio', 'run', '--target', 'checkprogsize']
    ]
    
    for cmd in pio_commands:
        try:
            print(f"Trying command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Compilation successful!")
                print("Program size information:")
                print(result.stdout)
                return True
            else:
                print(f"❌ Command failed with return code {result.returncode}")
                if result.stderr:
                    print("STDERR:", result.stderr[:500])  # First 500 chars
                    
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}")
            continue
        except subprocess.TimeoutExpired:
            print("Command timed out")
            continue
        except Exception as e:
            print(f"Error running command: {e}")
            continue
    
    print("\n❌ Could not compile with any PlatformIO command.")
    print("\nTo compile manually:")
    print("1. Open this project in PlatformIO IDE (VS Code)")
    print("2. Click the checkmark (✓) icon to build")
    print("3. Or use the PlatformIO terminal in VS Code")
    
    return False

def check_files():
    """
    Check if all required files are present
    """
    required_files = [
        'src/main.cpp',
        'platformio.ini',
        'include/model.h',
        'data/dashboard.html',
        'data/index.html'
    ]
    
    print("\nChecking required files:")
    all_present = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_present = False
    
    return all_present

def main():
    print("ESP32 WiFi Monitor - Compilation Test")
    print("=" * 40)
    
    # Check files first
    if not check_files():
        print("\n❌ Some required files are missing!")
        return 1
    
    # Test compilation
    if test_compilation():
        print("\n🎉 All tests passed! Your ESP32 code is ready to upload.")
        return 0
    else:
        print("\n⚠️  Compilation test failed, but you can still try building in PlatformIO IDE.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
