# EQ12 Coral Template Pack

This folder contains templates to help you run custom models on your Raspberry Pi with the Google Coral TPU.

## Files

*   `coral_runner.py`: A universal Python script for Image Classification and Object Detection.
*   `run_coral.sh`: A helper script to run the Python script inside the Docker container.

## Setup on Pi

1.  Create a folder for your project (e.g., `~/my_coral_project`).
2.  Copy these files into that folder.
3.  Make the shell script executable: `chmod +x run_coral.sh`.
4.  Download your `.tflite` model and labels file into the same folder.
5.  Place your input image in the folder.

## Usage

### Classification

```bash
./run_coral.sh --task classify \
    --model mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
    --labels inat_bird_labels.txt \
    --input parrot.jpg
```

### Object Detection

```bash
./run_coral.sh --task detect \
    --model ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite \
    --labels coco_labels.txt \
    --input street.jpg \
    --output annotated_street.jpg \
    --threshold 0.5
```

## Notes

*   The `run_coral.sh` script mounts the **current directory** (`$(pwd)`) to `/workspace` inside the container.
*   Ensure your model files and input images are in the current directory (or a subdirectory).
*   The output image (for detection) will be saved to the current directory.
