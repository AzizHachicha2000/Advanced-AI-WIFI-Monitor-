#!/usr/bin/env python3
"""
Fix the corrupted model.h file by properly converting the TensorFlow Lite model
"""

import os

def fix_model_header():
    print("🔧 Fixing corrupted model.h file...")
    
    # Read the TensorFlow Lite model
    if not os.path.exists('model.tflite'):
        print("❌ Error: model.tflite not found!")
        return False
        
    with open('model.tflite', 'rb') as f:
        model_data = f.read()
    
    model_size = len(model_data)
    print(f"📊 Model size: {model_size} bytes")
    
    # Generate proper C header content
    header_content = f"""#ifndef MODEL_H
#define MODEL_H

const unsigned int wifi_model_tflite_len = {model_size};
const unsigned char wifi_model_tflite[] = {{
"""
    
    # Add model data as hex bytes (16 bytes per line)
    for i, byte in enumerate(model_data):
        if i % 16 == 0:
            header_content += "  "
        
        header_content += f"0x{byte:02x}"
        
        if i < len(model_data) - 1:
            header_content += ", "
        
        if (i + 1) % 16 == 0:
            header_content += "\n"
    
    # Close the array and header
    if len(model_data) % 16 != 0:
        header_content += "\n"
    
    header_content += """};

#endif // MODEL_H
"""
    
    # Save the corrected header file
    with open('include/model.h', 'w') as f:
        f.write(header_content)
    
    print("✅ Fixed model.h successfully!")
    print(f"📁 Model header saved to: include/model.h")
    print(f"🎯 Model is now ready for ESP32 compilation!")
    
    return True

if __name__ == "__main__":
    success = fix_model_header()
    if success:
        print("\n🚀 You can now build your project without errors!")
    else:
        print("\n❌ Failed to fix model header. Check if model.tflite exists.")
