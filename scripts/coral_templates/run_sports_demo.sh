#!/bin/bash
# Wrapper to run the Sports Betting Edge Node inside the Docker container

# Ensure models exist
if [ ! -f "models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite" ]; then
    echo "Models not found. Running downloader..."
    bash get_sports_models.sh
fi

# Run the container
# We mount the current directory to /workspace
# We pass the USB device for TPU access
echo "Starting EQ12 Sports Edge Node..."

docker run --rm \
    --privileged \
    -v /dev/bus/usb:/dev/bus/usb \
    -v $(pwd):/workspace \
    -w /workspace \
    eq12-coral \
    python3 eq12_sports_edge.py \
    --model models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
    --labels models/coco_labels.txt \
    --input ${1:-models/soccer.jpg} \
    --cluster ${2:-192.168.1.100}
