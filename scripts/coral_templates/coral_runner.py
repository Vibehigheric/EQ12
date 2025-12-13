#!/usr/bin/env python3
"""
EQ12 Coral TPU Universal Runner
Supports Image Classification and Object Detection.
"""

import argparse
import time
import os
from PIL import Image
from PIL import ImageDraw

from pycoral.adapters import classify
from pycoral.adapters import detect
from pycoral.adapters import common
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

def draw_objects(draw, objs, labels):
    """Draws the bounding box and label for each object."""
    for obj in objs:
        bbox = obj.bbox
        draw.rectangle([(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax)],
                       outline='red')
        draw.text((bbox.xmin + 10, bbox.ymin + 10),
                  '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score),
                  fill='red')

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--model', required=True, help='File path of .tflite file')
    parser.add_argument('-l', '--labels', help='File path of labels file')
    parser.add_argument('-i', '--input', required=True, help='File path of image to process')
    parser.add_argument('-o', '--output', help='File path to save annotated image (Detection only)')
    parser.add_argument('-t', '--task', choices=['classify', 'detect'], default='classify', help='Task type')
    parser.add_argument('-k', '--top_k', type=int, default=3, help='Max results to show (Classification)')
    parser.add_argument('-c', '--count', type=int, default=5, help='Number of times to run inference (for benchmarking)')
    parser.add_argument('--threshold', type=float, default=0.4, help='Score threshold (Detection)')
    args = parser.parse_args()

    print(f"Loading model: {args.model}")
    interpreter = make_interpreter(args.model)
    interpreter.allocate_tensors()

    print(f"Loading labels: {args.labels}")
    labels = read_label_file(args.labels) if args.labels else {}

    print(f"Loading input: {args.input}")
    image = Image.open(args.input)
    _, scale = common.set_resized_input(interpreter, image.size, lambda size: image.resize(size, Image.LANCZOS))

    print("Running inference...")
    # Warmup
    interpreter.invoke()

    start = time.perf_counter()
    for _ in range(args.count):
        interpreter.invoke()
    inference_time = (time.perf_counter() - start) / args.count

    print(f"\nAverage Inference Time: {inference_time * 1000:.2f} ms")

    if args.task == 'classify':
        classes = classify.get_classes(interpreter, top_k=args.top_k)
        print("\nResults:")
        for c in classes:
            print(f"  {labels.get(c.id, c.id)}: {c.score:.5f}")
            
    elif args.task == 'detect':
        objs = detect.get_objects(interpreter, args.threshold, scale)
        print(f"\nDetected {len(objs)} objects:")
        for obj in objs:
            print(f"  {labels.get(obj.id, obj.id)}: {obj.score:.5f} (Box: {obj.bbox})")
        
        if args.output:
            image = image.convert('RGB')
            draw_objects(ImageDraw.Draw(image), objs, labels)
            image.save(args.output)
            print(f"\nSaved annotated image to: {args.output}")

if __name__ == '__main__':
    main()
