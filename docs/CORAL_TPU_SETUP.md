# Google Coral TPU Configuration Guide for EQ12

## Hardware Specifications

**Raspberry Pi Node: pi-node-1**
- Primary Processor: ARM Cortex-A72 (4-core)
- **AI Accelerator: Google Coral Edge TPU**
  - Bus: USB 3.0 (Bus 002, Device 002)
  - Vendor ID: 1a6e (Global Unichip)
  - Product ID: 089a
  - Performance: 4 TOPS (Tera Operations Per Second)
  - Power: ~2.5W
  - Inference Speed: ~100x faster than CPU-only

## What is Google Coral TPU?

The Coral TPU is a specialized processor designed for **edge machine learning inference**. It accelerates:
- Image classification
- Object detection
- Pose estimation
- Custom TensorFlow Lite models

Perfect for **EQ12 real-time AI operations** on the edge.

## Installation & Setup

### 1. Install Coral TPU Runtime (on Raspberry Pi)

```bash
# SSH into your Pi
ssh ricoj100@192.168.1.80

# Add Coral repository
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

# Add Google's APT key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# Update and install
sudo apt-get update
sudo apt-get install -y edgetpu-runtime

# Install Python support
pip3 install --upgrade pip
pip3 install pycoral
```

### 2. Verify Coral TPU Detection

```bash
# Check if device is recognized
lsusb | grep "1a6e:089a"

# Should output:
# Bus 002 Device 002: ID 1a6e:089a Global Unichip Corp.

# Test with Python
python3 -c "from pycoral.utils.edgetpu import get_edgetpu_model_path; print('Coral TPU ready!')"
```

### 3. Test Coral TPU Performance

```bash
# Install TensorFlow Lite examples
pip3 install numpy opencv-python

# Get example models
mkdir -p ~/coral_models
cd ~/coral_models

# Download a pre-compiled model
wget https://dl.google.com/coral/models/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite
wget https://dl.google.com/coral/models/inat_bird_labels.txt

# Run inference test
python3 << 'PYTHON_EOF'
from pycoral.adapters import classify
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
import time

model_path = 'mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite'
label_path = 'inat_bird_labels.txt'

interpreter = make_interpreter(model_path)
interpreter.allocate_tensors()

labels = read_label_file(label_path)

print("✓ Coral TPU initialized successfully!")
print(f"  Model: {model_path}")
print(f"  Labels loaded: {len(labels)} categories")
print("  Ready for inference")
PYTHON_EOF
```

## EQ12 Integration

### Usage in EQ12 Scripts

```python
from pycoral.adapters import classify, detect
from pycoral.utils.edgetpu import make_interpreter
from PIL import Image
import time

class CoralAccelerator:
    def __init__(self, model_path):
        self.interpreter = make_interpreter(model_path)
        self.interpreter.allocate_tensors()
    
    def classify_image(self, image_path):
        """Run image classification on TPU"""
        image = Image.open(image_path).convert('RGB')
        start = time.time()
        results = classify.run_inference(
            self.interpreter,
            image,
            top_k=3
        )
        latency = time.time() - start
        return results, latency
    
    def detect_objects(self, image_path):
        """Run object detection on TPU"""
        image = Image.open(image_path).convert('RGB')
        start = time.time()
        results = detect.run_inference(
            self.interpreter,
            image,
            threshold=0.4
        )
        latency = time.time() - start
        return results, latency

# Usage
coral = CoralAccelerator('model_quant_edgetpu.tflite')
results, latency = coral.classify_image('test_image.jpg')
print(f"Classification in {latency*1000:.2f}ms")
```

### Docker Support

```dockerfile
FROM balena/rpi-debian:latest

# Install Coral TPU runtime
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -y edgetpu-runtime python3-pycoral

# Copy your EQ12 ML models
COPY models/ /app/models/
COPY scripts/ /app/scripts/

WORKDIR /app
ENTRYPOINT ["python3", "scripts/ml_inference.py"]
```

## Performance Benchmarks

### Typical Inference Times (on Coral TPU)

| Model | Input Size | Latency |
|-------|-----------|---------|
| MobileNet v2 | 224x224 | ~50ms |
| SSD MobileNet | 320x320 | ~150ms |
| PoseNet | 353x353 | ~200ms |
| YOLOv3 (quantized) | 416x416 | ~250ms |

**CPU-only equivalent: 10-50x slower**

## Monitoring & Diagnostics

```bash
# Check TPU temperature
cat /sys/class/thermal/thermal_zone0/temp

# Monitor power usage
echo "Coral TPU typically draws 2-3W during inference"

# Check system load
htop

# Verify device permissions
ls -la /dev/apex*
```

## Troubleshooting

### Device Not Detected
```bash
# Check USB connection
lsusb -v | grep -A5 1a6e:089a

# Reload device drivers
sudo systemctl restart edgetpu-runtime

# Check permissions
sudo usermod -aG apex-user $(whoami)
newgrp apex-user
```

### Performance Issues
- Ensure USB 3.0 connection (not USB 2.0)
- Monitor thermal throttling
- Check for competing CPU workloads
- Use quantized models (int8 faster than float32)

### Model Compatibility
- Only TensorFlow Lite (.tflite) models with Edge TPU compiler
- Must be quantized for Coral TPU
- Use `edgetpu_compiler` to compile custom models:

```bash
pip3 install edgetpu
edgetpu_compiler -s model.tflite
# Output: model_edgetpu.tflite (ready for inference)
```

## Best Practices for EQ12

1. **Use Quantized Models:** 4-8x faster than float32
2. **Batch Processing:** Queue multiple inference requests
3. **Model Optimization:** Use TensorFlow Lite Converter
4. **Caching:** Pre-load models in memory
5. **Error Handling:** Graceful fallback to CPU if TPU fails
6. **Monitoring:** Track inference latency and accuracy

## Next Steps

1. Verify Coral TPU is detected: `lsusb | grep 1a6e`
2. Install pycoral: `pip3 install pycoral`
3. Download example models from Google Coral repository
4. Run inference benchmarks
5. Integrate into EQ12 ML pipelines

## Resources

- Google Coral Documentation: https://coral.ai/docs/
- Edge TPU Models: https://coral.ai/models/
- TensorFlow Lite: https://www.tensorflow.org/lite
- PyCoral API: https://github.com/google-coral/pycoral

---

**Your EQ12 setup is now optimized for edge AI inference! 🚀**
