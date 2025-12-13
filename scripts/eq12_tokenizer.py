#!/usr/bin/env python3
"""
 EQ12 Production-Grade Tokenization Layer for Coral TPU
Converts messy sports/crypto/news feeds into wire-speed uint8 tensors

FEATURES:
- Fixed-shape uint8 tensors (Edge TPU optimized)
- Deterministic tabular/categorical/text encoding
- Zero-dependency text sketching with feature hashing
- Production-ready with frozen scaling parameters
"""

import re
import math
import json
import time
import hashlib
from collections import Counter
from typing import Dict, List, Any, Optional
import numpy as np
import yaml
import argparse
import pathlib
from datetime import datetime
import logging

# Import player availability gatekeeper
try:
    from eq12_player_availability import PlayerAvailabilityManager
    AVAILABILITY_CHECK_ENABLED = True
except ImportError:
    AVAILABILITY_CHECK_ENABLED = False

# Fast regex for text normalization
NONALNUM = re.compile(r"[^a-z0-9\s]+")

def mmh(s: str) -> int:
    """MurmurHash replacement using BLAKE2b for deterministic hashing"""
    return int(hashlib.blake2b(s.encode("utf-8"), digest_size=8).hexdigest(), 16)

def normalize_uint8(x: float, a: float, b: float) -> int:
    """Scale numeric value to uint8 range [0, 255] with frozen min/max bounds"""
    if a == b:
        return 0
    v = int(round(255.0 * (max(min(x, b), a) - a) / (b - a)))
    return max(0, min(255, v))

def ngrams(tokens: List[str], n: int):
    """Generate n-grams from token list"""
    for i in range(len(tokens) - n + 1):
        yield " ".join(tokens[i:i+n])

def text_sketch(text: str, slots: int = 190) -> np.ndarray:
    """
    Fast text  uint8 vector using feature hashing
    - Normalize text  tokenize  1,2,3-grams  hash into fixed slots
    - Collision-tolerant, deterministic, zero external deps
    """
    text = NONALNUM.sub(" ", text.lower()).strip()
    toks = text.split()
    feats = Counter()
    
    # Generate 1,2,3-grams and hash into feature slots
    for n in (1, 2, 3):
        for g in ngrams(toks, n):
            feats[mmh(g) % slots] += 1
    
    # Convert to uint8 array with count capping
    arr = np.zeros(slots, dtype=np.uint8)
    for k, v in feats.items():
        arr[k] = 255 if v > 255 else v
    
    return arr


class EQ12Tokenizer:
    """
     Production tokenizer for Coral TPU inference
    Converts sports/crypto feeds to fixed-shape uint8 tensors
    """
    
    def __init__(self, cfg_path: str):
        """Initialize tokenizer with frozen scaling parameters"""
        with open(cfg_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f" EQ12 Tokenizer initialized from {cfg_path}")
        
        # Initialize player availability manager
        if AVAILABILITY_CHECK_ENABLED:
            try:
                workspace_path = str(pathlib.Path(cfg_path).parent.parent)
                self.availability_manager = PlayerAvailabilityManager(workspace_path)
                self.logger.info(" Player availability gatekeeper enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize availability manager: {e}")
                self.availability_manager = None
        else:
            self.availability_manager = None
    
    def _num_block(self, row: Dict[str, Any], spec: List[Dict[str, Any]]) -> List[int]:
        """Process numeric features with frozen min/max scaling"""
        out = []
        for f in spec:
            name = f["name"]
            a = float(f["min"])
            b = float(f["max"])
            default_val = float(f.get("default", a))
            
            x = row.get(name, default_val)
            try:
                x = float(x)
                # Handle inf and nan values
                if not np.isfinite(x):
                    x = default_val
            except (ValueError, TypeError):
                x = default_val
            
            out.append(normalize_uint8(float(x), a, b))
        
        return out
    
    def _cat_block(self, row: Dict[str, Any], spec: List[Dict[str, Any]]) -> List[int]:
        """Process categorical features with hash bucketing"""
        out = []
        for f in spec:
            name = f["name"]
            B = int(f.get("buckets", 8))
            
            val = str(row.get(name, "UNK")).lower().strip()
            bucket = mmh(name + ":" + val) % B
            
            # One-hot encoding compressed to uint8 (0 or 255)
            vec = [0] * B
            vec[bucket] = 255
            out.extend(vec)
        
        return out
    
    def sports(self, row: Dict[str, Any]) -> np.ndarray:
        """
         Sports tokenization: odds/props/news  [256] uint8
        
        Input: betting line dictionary
        Output: fixed-shape uint8 tensor for Coral TPU
        """
        #  GATEKEEPER: Check player availability first
        player_name = row.get("player_name", "")
        if player_name and self.availability_manager:
            if not self.availability_manager.is_player_available(player_name):
                self.logger.warning(f" Skipping unavailable player: {player_name}")
                return np.zeros(self.cfg["sports"]["dim"], dtype=np.uint8)
        
        # Process numeric features (odds, spreads, weather, etc.)
        num = self._num_block(row, self.cfg["sports"]["numeric"])
        
        # Process categorical features (teams, books, markets)
        cat = self._cat_block(row, self.cfg["sports"]["categorical"])
        
        # Process text features (headlines, injury notes)
        text_content = " ".join([
            str(row.get("headline", "")),
            str(row.get("note", "")),
            str(row.get("injury", "")),
            str(row.get("weather_desc", ""))
        ])
        
        txt = text_sketch(text_content, slots=self.cfg["sports"]["text_slots"])
        
        # Combine all features
        vec = np.array(num + cat, dtype=np.uint8)
        final_vec = np.concatenate([vec, txt])[:self.cfg["sports"]["dim"]]
        
        # Pad to exact dimension if needed
        if len(final_vec) < self.cfg["sports"]["dim"]:
            pad_size = self.cfg["sports"]["dim"] - len(final_vec)
            padding = np.zeros(pad_size, dtype=np.uint8)
            final_vec = np.concatenate([final_vec, padding])
        
        return final_vec
    
    def crypto(self, row: Dict[str, Any]) -> np.ndarray:
        """
         Crypto tokenization: OHLCV/news/sentiment  [256] uint8
        
        Input: crypto market data dictionary
        Output: fixed-shape uint8 tensor for Coral TPU
        """
        # Process numeric features (prices, volumes, indicators)
        num = self._num_block(row, self.cfg["crypto"]["numeric"])
        
        # Process categorical features (exchange, symbols)
        cat = self._cat_block(row, self.cfg["crypto"]["categorical"])
        
        # Process text features (news, sentiment)
        text_content = " ".join([
            str(row.get("news_title", "")),
            str(row.get("news_summary", "")),
            str(row.get("sentiment_text", ""))
        ])
        
        txt = text_sketch(text_content, slots=self.cfg["crypto"]["text_slots"])
        
        # Combine all features
        vec = np.array(num + cat, dtype=np.uint8)
        final_vec = np.concatenate([vec, txt])[:self.cfg["crypto"]["dim"]]
        
        # Pad to exact dimension if needed
        if len(final_vec) < self.cfg["crypto"]["dim"]:
            padding = np.zeros(self.cfg["crypto"]["dim"] - len(final_vec), dtype=np.uint8)
            final_vec = np.concatenate([final_vec, padding])
        
        return final_vec
    
    def batch_tokenize(self, data: List[Dict[str, Any]], mode: str) -> np.ndarray:
        """
         Batch tokenization for high-throughput processing
        """
        tokenizer_func = self.sports if mode == "sports" else self.crypto
        
        vectors = []
        for row in data:
            try:
                vec = tokenizer_func(row)
                vectors.append(vec)
            except Exception as e:
                self.logger.warning(f"Failed to tokenize row: {e}")
                # Add zero vector for failed tokenization
                dim = self.cfg[mode]["dim"]
                vectors.append(np.zeros(dim, dtype=np.uint8))
        
        if not vectors:
            dim = self.cfg[mode]["dim"]
            return np.zeros((0, dim), dtype=np.uint8)
        
        return np.stack(vectors)
    
    def validate_output(self, tensor: np.ndarray, mode: str) -> bool:
        """Validate output tensor meets Coral TPU requirements"""
        expected_dim = self.cfg[mode]["dim"]
        
        # Check shape
        if len(tensor.shape) != 2 or tensor.shape[1] != expected_dim:
            self.logger.error(f"Invalid tensor shape: {tensor.shape}, expected [N, {expected_dim}]")
            return False
        
        # Check dtype
        if tensor.dtype != np.uint8:
            self.logger.error(f"Invalid dtype: {tensor.dtype}, expected uint8")
            return False
        
        # Check value range
        if tensor.min() < 0 or tensor.max() > 255:
            self.logger.error(f"Values out of range: [{tensor.min()}, {tensor.max()}]")
            return False
        
        return True


def setup_logging(verbose: bool = False):
    """Configure logging for tokenizer"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    parser = argparse.ArgumentParser(description="EQ12 Production Tokenizer for Coral TPU")
    parser.add_argument("--cfg", default="C:/EQ12/configs/eq12_tokenizer.yaml",
                        help="Tokenizer configuration file")
    parser.add_argument("--mode", choices=["sports", "crypto"], required=True,
                        help="Tokenization mode")
    parser.add_argument("--in_json", required=True,
                        help="Input LDJSON file (line-delimited JSON records)")
    parser.add_argument("--out_npz", required=True,
                        help="Output NPZ file for tokenized tensors")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose logging")
    parser.add_argument("--validate", action="store_true",
                        help="Validate output tensor")
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    print(f" EQ12 Production Tokenizer - {args.mode.upper()} Mode")
    print(f" Processing: {args.in_json}")
    print(f" Output: {args.out_npz}")
    
    # Initialize tokenizer
    try:
        tok = EQ12Tokenizer(args.cfg)
    except Exception as e:
        logger.error(f"Failed to initialize tokenizer: {e}")
        return 1
    
    # Process input data
    data = []
    try:
        with open(args.in_json, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    row = json.loads(line)
                    data.append(row)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON on line {line_num}: {e}")
                    continue
    
    except FileNotFoundError:
        logger.error(f"Input file not found: {args.in_json}")
        return 1
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        return 1
    
    if not data:
        logger.warning("No valid data found in input file")
        X = np.zeros((0, tok.cfg[args.mode]["dim"]), dtype=np.uint8)
    else:
        logger.info(f" Tokenizing {len(data)} records...")
        start_time = time.time()
        
        X = tok.batch_tokenize(data, args.mode)
        
        processing_time = time.time() - start_time
        logger.info(f" Tokenized {len(data)} records in {processing_time:.2f}s")
        logger.info(f" Throughput: {len(data)/processing_time:.0f} records/sec")
    
    # Validate output if requested
    if args.validate and not tok.validate_output(X, args.mode):
        logger.error("Output validation failed")
        return 1
    
    # Save tokenized data
    try:
        pathlib.Path(args.out_npz).parent.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'X': X,
            'timestamp': int(time.time()),
            'mode': args.mode,
            'config_file': args.cfg,
            'input_file': args.in_json,
            'shape': X.shape,
            'dtype': str(X.dtype)
        }
        
        np.savez_compressed(args.out_npz, **metadata)
        
        print(f" Saved tensor shape {X.shape}  {args.out_npz}")
        print(f" Ready for Coral TPU inference!")
        
        logger.info(f"Tokenization complete: {X.shape}  {args.out_npz}")
        
    except Exception as e:
        logger.error(f"Failed to save output: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())