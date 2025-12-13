#!/usr/bin/env python3
"""
EQ12 Sports Betting Edge Node (Coral TPU)
-----------------------------------------
This script runs on the Raspberry Pi + Coral TPU.
It analyzes visual data (frames) to detect game events (players, balls)
and transmits structured data to the EQ12 Cluster for betting decisions.

Usage:
    python3 eq12_sports_edge.py --model <model_path> --labels <label_path> --input <image_path> --cluster <cluster_ip>
"""

import argparse
import time
import json
import sys
from PIL import Image
from pycoral.adapters import detect
from pycoral.adapters import common
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True, help='Path to .tflite detection model')
    parser.add_argument('--labels', required=True, help='Path to label map')
    parser.add_argument('--input', required=True, help='Input image (simulating live frame)')
    parser.add_argument('--cluster', default='192.168.1.100', help='EQ12 Cluster IP to receive signals')
    parser.add_argument('--threshold', type=float, default=0.4, help='Detection threshold')
    args = parser.parse_args()

    # 1. Initialize TPU
    print("[Edge] Initializing Coral TPU...")
    interpreter = make_interpreter(args.model)
    interpreter.allocate_tensors()
    labels = read_label_file(args.labels)

    # 2. Load Frame
    print(f"[Edge] Analyzing frame: {args.input}")
    image = Image.open(args.input)
    _, scale = common.set_resized_input(interpreter, image.size, lambda size: image.resize(size, Image.LANCZOS))

    # 3. Run Inference (High Speed)
    start = time.perf_counter()
    interpreter.invoke()
    objs = detect.get_objects(interpreter, args.threshold, scale)
    inference_time = (time.perf_counter() - start) * 1000

    # 4. Analyze Game State
    game_state = {
        "timestamp": time.time(),
        "inference_ms": inference_time,
        "detected_entities": [],
        "betting_signal": "HOLD"
    }

    player_count = 0
    ball_detected = False

    for obj in objs:
        label = labels.get(obj.id, obj.id)
        game_state["detected_entities"].append({
            "id": obj.id,
            "label": label,
            "score": float(obj.score),
            "bbox": [obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax]
        })
        
        if "person" in str(label).lower():
            player_count += 1
        if "ball" in str(label).lower():
            ball_detected = True

    # 5. Generate Betting Signal (Simple Logic)
    # Example: If we see many players and a ball, the game is active.
    if player_count > 2 and ball_detected:
        game_state["betting_signal"] = "LIVE_PLAY_ACTIVE"
    elif player_count == 0:
        game_state["betting_signal"] = "BREAK_OR_TIMEOUT"

    # 6. Transmit to Cluster
    payload = json.dumps(game_state)
    print(f"\n[Edge] >>> SIGNAL TRANSMITTED TO {args.cluster} >>>")
    print(payload)
    print("---------------------------------------------------")
    
    # In a real scenario, we would do:
    # requests.post(f"http://{args.cluster}:8000/ingest", json=game_state)

if __name__ == '__main__':
    main()
