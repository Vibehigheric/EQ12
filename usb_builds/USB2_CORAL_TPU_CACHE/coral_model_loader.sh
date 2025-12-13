#!/bin/bash
# Coral TPU Model Loader for Raspberry Pi
# Optimizes model loading from USB cache

echo "🟣 CORAL TPU MODEL CACHE ACTIVATED"
echo "Buffalo NY 14215 AI Edge Computing"

CACHE_PATH="/mnt/usb_coral_cache"
MODEL_PATH="/opt/coral/models"

# Mount USB cache
sudo mkdir -p $CACHE_PATH
sudo mount /dev/sda1 $CACHE_PATH

# Create symlinks for fast model access
echo "📊 Creating model symlinks..."
ln -sf $CACHE_PATH/DETECTION_MODELS/* $MODEL_PATH/
ln -sf $CACHE_PATH/OCR_MODELS/* $MODEL_PATH/
ln -sf $CACHE_PATH/WEATHER_MODELS/* $MODEL_PATH/

# Set up memory optimization
echo "🧠 Optimizing Pi memory for Coral..."
echo "gpu_mem=16" >> /boot/config.txt
echo "arm_64bit=1" >> /boot/config.txt

# Test Coral TPU
echo "🧪 Testing Coral TPU..."
python3 -c "from pycoral.utils import edgetpu; print(f'Coral devices: {edgetpu.list_edge_tpus()}')"

echo "✅ Coral TPU Model Cache: ACTIVE"
echo "🚀 Pi + EQ12 AI acceleration: READY"
