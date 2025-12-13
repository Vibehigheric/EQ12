#!/bin/bash
# Download models optimized for Coral TPU (Sports/Object Detection)

mkdir -p models

echo "Downloading SSD MobileNet V2 (COCO)..."
curl -L -o models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
    https://github.com/google-coral/test_data/raw/master/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite

echo "Downloading COCO Labels..."
curl -L -o models/coco_labels.txt \
    https://github.com/google-coral/test_data/raw/master/coco_labels.txt

echo "Downloading sample sports image..."
curl -L -o models/soccer.jpg \
    https://raw.githubusercontent.com/google-coral/test_data/master/grace_hopper.bmp 
    # (Using placeholder, user should provide real sports image)

echo "Done. Models saved to ./models/"
