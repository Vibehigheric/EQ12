import os
import time
import urllib.request
import numpy as np
from PIL import Image
from pycoral.adapters import classify
from pycoral.adapters import common
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

# Constants
MODEL_URL = 'https://github.com/google-coral/test_data/raw/master/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite'
LABEL_URL = 'https://github.com/google-coral/test_data/raw/master/inat_bird_labels.txt'
IMAGE_URL = 'https://github.com/google-coral/test_data/raw/master/parrot.jpg'

MODEL_FILE = 'mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite'
LABEL_FILE = 'inat_bird_labels.txt'
IMAGE_FILE = 'parrot.jpg'

def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print("Done.")

def main():
    print("=== Coral TPU Model Test ===")
    
    # Check devices first
    from pycoral.utils.edgetpu import list_edge_tpus
    print("Checking for Edge TPU devices...")
    devs = list_edge_tpus()
    print(f"Detected devices: {devs}")
    
    if not devs:
        print("ERROR: No Edge TPU devices found.")
        return

    # Download resources
    try:
        download_file(MODEL_URL, MODEL_FILE)
        download_file(LABEL_URL, LABEL_FILE)
        download_file(IMAGE_URL, IMAGE_FILE)
    except Exception as e:
        print(f"Error downloading files: {e}")
        return

    # Initialize interpreter
    print(f"Loading model: {MODEL_FILE}")
    try:
        # Try explicit device selection if multiple or just to be safe
        interpreter = make_interpreter(MODEL_FILE)
        interpreter.allocate_tensors()
    except Exception as e:
        print(f"Error initializing TPU: {e}")
        import traceback
        traceback.print_exc()
        return

    # Prepare image
    print(f"Loading image: {IMAGE_FILE}")
    size = common.input_size(interpreter)
    try:
        image = Image.open(IMAGE_FILE).convert('RGB').resize(size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
    except Exception as e:
        print(f"Error processing image: {e}")
        return

    # Run inference
    print("Running inference...")
    common.set_input(interpreter, image)
    
    # Warmup
    print("Warmup run...")
    interpreter.invoke()
    
    # Benchmark
    print("Benchmark run...")
    start = time.perf_counter()
    interpreter.invoke()
    inference_time = time.perf_counter() - start
    
    classes = classify.get_classes(interpreter, top_k=3)
    labels = read_label_file(LABEL_FILE)

    print('\n------- RESULTS --------')
    for c in classes:
        print(f'{labels.get(c.id, c.id)}: {c.score:.5f}')
    print(f'Inference time: {inference_time*1000:.2f} ms')
    print('------------------------')

if __name__ == '__main__':
    main()
