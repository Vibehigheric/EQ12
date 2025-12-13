#!/usr/bin/env python3
# Download and cache Coral TPU models
import requests
import os
from pathlib import Path

def download_model(url: str, filename: str, directory: str):
    """Download model to cache directory"""
    cache_dir = Path(directory)
    cache_dir.mkdir(exist_ok=True)
    
    model_path = cache_dir / filename
    if model_path.exists():
        print(f" {filename} already cached")
        return
    
    print(f" Downloading {filename}...")
    response = requests.get(url)
    with open(model_path, 'wb') as f:
        f.write(response.content)
    print(f" {filename} cached")

# Essential Coral models
models = [
    ("https://github.com/google-coral/test_data/raw/master/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite", "bird_detection.tflite", "DETECTION_MODELS"),
    ("https://github.com/google-coral/test_data/raw/master/mobilenet_v2_1.0_224_quant_edgetpu.tflite", "image_classification.tflite", "DETECTION_MODELS"),
    ("https://github.com/google-coral/test_data/raw/master/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite", "object_detection.tflite", "DETECTION_MODELS")
]

for url, filename, directory in models:
    download_model(url, filename, directory)

print(" Coral model cache ready for Pi deployment!")
