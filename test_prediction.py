#!/usr/bin/env python3
"""
Test script to compare rule-based prediction with trained TensorFlow model
"""

import pandas as pd
import numpy as np
import tensorflow as tf

def rule_based_prediction(rssi, noise, snr, channel_util):
    """
    Rule-based stability prediction (same logic as ESP32 code)
    """
    stability = 0.0
    
    if rssi > -70:
        stability += 0.4
    if snr > 20:
        stability += 0.3
    if channel_util < 50:
        stability += 0.3
    
    return stability

def test_predictions():
    """
    Test the TensorFlow Lite model predictions on sample data
    """
    # Load the trained model
    try:
        interpreter = tf.lite.Interpreter(model_path='model.tflite')
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        print("🤖 TensorFlow Lite model loaded successfully!")
        print(f"📊 Model input shape: {input_details[0]['shape']}")
        print(f"📈 Model output shape: {output_details[0]['shape']}")
        ml_available = True
    except Exception as e:
        print(f"❌ TensorFlow Lite model not available: {e}")
        ml_available = False
    
    # Load test data
    try:
        df = pd.read_csv('wifi_data.csv')
        print(f"Loaded {len(df)} test samples")
    except FileNotFoundError:
        print("No test data found. Run generate_dataset.py first.")
        return
    
    # Test on first 10 samples
    print("\nTesting predictions on sample data:")
    print("RSSI\tNoise\tSNR\tChan%\tActual\tRule\tML")
    print("-" * 60)
    
    correct_rule = 0
    correct_ml = 0
    
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        rssi = row['rssi']
        noise = row['noise']
        snr = row['snr']
        channel_util = row['channel_util']
        actual = row['stability']
        
        # Rule-based prediction
        rule_pred = rule_based_prediction(rssi, noise, snr, channel_util)
        rule_binary = 1 if rule_pred > 0.5 else 0
        
        # ML prediction
        if ml_available:
            # Normalize inputs (same as training)
            input_data = np.array([[
                (rssi + 90) / 30.0,
                noise / 50.0,
                (snr + 40) / 60.0,
                channel_util / 100.0
            ]], dtype=np.float32)
            
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            ml_pred = interpreter.get_tensor(output_details[0]['index'])[0][0]
            ml_binary = 1 if ml_pred > 0.5 else 0
        else:
            ml_pred = 0
            ml_binary = 0
        
        # Check accuracy
        if rule_binary == actual:
            correct_rule += 1
        if ml_binary == actual:
            correct_ml += 1
        
        print(f"{rssi:.1f}\t{noise:.1f}\t{snr:.1f}\t{channel_util:.1f}\t{actual}\t{rule_pred:.2f}\t{ml_pred:.2f}")
    
    print(f"\nRule-based accuracy: {correct_rule}/10 = {correct_rule*10}%")
    if ml_available:
        print(f"ML accuracy: {correct_ml}/10 = {correct_ml*10}%")

if __name__ == "__main__":
    test_predictions()
