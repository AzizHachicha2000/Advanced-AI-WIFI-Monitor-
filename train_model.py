import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

print("🚀 Advanced AI WiFi Stability Model Training")
print("=" * 50)

# Load and prepare data
print("📊 Loading training data...")
df = pd.read_csv('wifi_data.csv')
print(f"Dataset size: {len(df)} samples")

# Keep ONLY the 4 basic features as requested
print("🔧 Using ONLY the 4 basic features (RSSI, Noise, SNR, Channel Utilization)...")

# Original 4 features ONLY - no additional feature engineering
X_base = df[['rssi', 'noise', 'snr', 'channel_util']].copy()

print(f"Using exactly 4 features as requested: {list(X_base.columns)}")

y = df['stability']

# Advanced Normalization (this is where we make it advanced)
print("📏 Applying advanced robust normalization...")
scaler = RobustScaler()  # More robust to outliers than StandardScaler
X_scaled = scaler.fit_transform(X_base)

# Split data with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")

# Advanced Neural Network Architecture (using ONLY 4 features but with sophisticated architecture)
print("🧠 Building advanced neural network with sophisticated architecture...")
print("📊 Input: ONLY 4 features (RSSI, Noise, SNR, Channel Utilization)")

# Create an efficient but advanced model with 4 layers (perfect for ESP32)
def create_advanced_model(input_dim):
    model = tf.keras.Sequential([
        # Layer 1: Input Processing (32 neurons)
        tf.keras.layers.Dense(32, activation='relu', input_shape=(input_dim,)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.2),

        # Layer 2: Hidden Layer (16 neurons)
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.15),

        # Layer 3: Hidden Layer (8 neurons)
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dropout(0.1),

        # Layer 4: Output Layer (1 neuron)
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    return model

model = create_advanced_model(X_scaled.shape[1])

# Advanced compilation with custom metrics
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy', 'precision', 'recall']
)

print("📋 Model Architecture:")
model.summary()

# Advanced training with callbacks
print("🏋️ Training advanced model...")

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-6
    )
]

history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=32,
    validation_data=(X_test, y_test),
    callbacks=callbacks,
    verbose=1
)

# Evaluate model
print("\n📊 Model Evaluation:")
test_loss, test_accuracy, test_precision, test_recall = model.evaluate(X_test, y_test, verbose=0)
print(f"Test Accuracy: {test_accuracy:.4f}")
print(f"Test Precision: {test_precision:.4f}")
print(f"Test Recall: {test_recall:.4f}")

# Detailed predictions analysis
y_pred_proba = model.predict(X_test)
y_pred = (y_pred_proba > 0.5).astype(int)

print("\n📈 Classification Report:")
print(classification_report(y_test, y_pred))

# Convert to TensorFlow Lite with optimization
print("🔄 Converting to TensorFlow Lite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]  # Use float16 for smaller model
tflite_model = converter.convert()

# Save the optimized model
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)

print(f"✅ Advanced model saved! Size: {len(tflite_model)} bytes")

# Save the scaler for use in ESP32
import pickle
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("✅ Scaler saved for ESP32 integration")
print("🎯 Advanced AI model training complete!")

# Convert to C header (Windows compatible)
def create_c_header(tflite_file, header_file):
    with open(tflite_file, 'rb') as f:
        data = f.read()

    with open(header_file, 'w') as f:
        f.write('#ifndef MODEL_H\n')
        f.write('#define MODEL_H\n\n')
        f.write('const unsigned char wifi_model_tflite[] = {\n')

        for i, byte in enumerate(data):
            if i % 12 == 0:
                f.write('  ')
            f.write(f'0x{byte:02x}')
            if i < len(data) - 1:
                f.write(', ')
            if (i + 1) % 12 == 0:
                f.write('\n')

        if len(data) % 12 != 0:
            f.write('\n')

        f.write('};\n')
        f.write(f'const unsigned int wifi_model_tflite_len = {len(data)};\n\n')
        f.write('#endif // MODEL_H\n')

create_c_header('model.tflite', 'include/model.h')
print("Model trained and converted to include/model.h")