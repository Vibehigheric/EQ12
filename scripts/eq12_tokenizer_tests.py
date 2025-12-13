#!/usr/bin/env python3
"""
 EQ12 Tokenizer Test Suite & Sample Data Generator
Production-grade testing for Coral TPU tokenization pipeline
"""

import json
import random
import time
import numpy as np
from datetime import datetime
from pathlib import Path
import sys
import os

# Add scripts directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from eq12_tokenizer import EQ12Tokenizer, text_sketch, normalize_uint8, mmh
except ImportError as e:
    print(f" Failed to import tokenizer: {e}")
    print("Make sure eq12_tokenizer.py is in the same directory")
    sys.exit(1)


class TokenizerTestSuite:
    """ Comprehensive test suite for tokenizer validation"""
    
    def __init__(self, workspace: str = "C:/EQ12"):
        self.workspace = Path(workspace)
        self.config_path = self.workspace / "configs" / "eq12_tokenizer.yaml"
        self.test_data_path = self.workspace / "test_data"
        self.test_data_path.mkdir(exist_ok=True)
        
        # Initialize tokenizer
        if not self.config_path.exists():
            print(f" Config file not found: {self.config_path}")
            sys.exit(1)
        
        self.tokenizer = EQ12Tokenizer(str(self.config_path))
        print(f" Tokenizer initialized from {self.config_path}")
    
    def generate_sports_sample(self, count: int = 100) -> str:
        """Generate sample sports betting data"""
        print(f" Generating {count} sports betting samples...")
        
        teams = ["LAL", "GSW", "BOS", "MIA", "DEN", "PHX", "MIL", "BKN", "DAL", "PHI"]
        markets = ["moneyline", "spread", "total", "player_props", "team_props"]
        books = ["draftkings", "fanduel", "mgm", "caesars", "betrivers"]
        
        samples = []
        for i in range(count):
            sample = {
                # Betting data
                "moneyline": random.randint(-500, 500),
                "spread": round(random.uniform(-15, 15), 1),
                "total": round(random.uniform(190, 250), 1),
                "implied_prob": round(random.uniform(0.2, 0.8), 3),
                "kelly_frac": round(random.uniform(0, 0.3), 3),
                
                # Team performance
                "pace": round(random.uniform(95, 110), 1),
                "dvoa_off": round(random.uniform(-20, 20), 1),
                "dvoa_def": round(random.uniform(-20, 20), 1),
                "rating_off": round(random.uniform(90, 120), 1),
                "rating_def": round(random.uniform(90, 120), 1),
                
                # Environmental
                "temp_f": random.randint(45, 85),
                "wind_mph": random.randint(0, 15),
                "humidity": random.randint(30, 80),
                "rest_days": random.randint(0, 7),
                
                # Market dynamics
                "line_age_min": random.randint(5, 300),
                "volume_ratio": round(random.uniform(0.5, 3.0), 2),
                "sharp_money": round(random.uniform(0.2, 0.8), 2),
                "public_pct": round(random.uniform(0.3, 0.7), 2),
                
                # Player props
                "usage_rate": round(random.uniform(15, 35), 1),
                "minutes_proj": round(random.uniform(20, 40), 1),
                
                # Categorical
                "team_home": random.choice(teams),
                "team_away": random.choice(teams),
                "market": random.choice(markets),
                "sportsbook": random.choice(books),
                "league": "NBA",
                "game_type": random.choice(["regular", "playoff", "preseason"]),
                "venue_type": "indoor",
                
                # Text data
                "headline": f"{random.choice(teams)} vs {random.choice(teams)} injury report",
                "note": f"Key player {random.choice(['questionable', 'probable', 'out'])}",
                "injury": random.choice(["ankle sprain", "knee soreness", "rest", ""]),
                "weather_desc": "clear conditions"
            }
            samples.append(sample)
        
        # Save as LDJSON
        sports_file = self.test_data_path / "sports_sample.ldjson"
        with open(sports_file, 'w') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')
        
        print(f" Saved {count} sports samples to {sports_file}")
        return str(sports_file)
    
    def generate_crypto_sample(self, count: int = 100) -> str:
        """Generate sample crypto market data"""
        print(f" Generating {count} crypto market samples...")
        
        bases = ["BTC", "ETH", "SOL", "ADA", "AVAX", "MATIC", "DOT", "LINK"]
        quotes = ["USD", "USDT", "USDC", "BTC", "ETH"]
        exchanges = ["coinbase", "binance", "kraken", "ftx", "okx"]
        sectors = ["L1", "DEFI", "NFT", "GAMING", "MEME", "ORACLE"]
        
        samples = []
        for i in range(count):
            base_price = random.uniform(0.01, 50000)
            
            sample = {
                # Price and volume
                "price_usd": base_price,
                "volume_24h": random.uniform(1e6, 1e10),
                "market_cap": random.uniform(1e7, 1e11),
                
                # Technical indicators  
                "rsi_14": round(random.uniform(20, 80), 1),
                "bb_position": round(random.uniform(0.1, 0.9), 2),
                "macd_signal": round(random.uniform(-100, 100), 2),
                
                # Volatility
                "vol_1m": round(random.uniform(0.1, 3.0), 3),
                "vol_5m": round(random.uniform(0.2, 4.0), 3),
                "vol_1h": round(random.uniform(0.5, 6.0), 3),
                
                # Order book
                "ob_imbalance": round(random.uniform(-0.5, 0.5), 3),
                "spread_bps": round(random.uniform(1, 20), 1),
                "depth_ratio": round(random.uniform(0.5, 2.0), 2),
                
                # Returns
                "ret_1m": round(random.uniform(-1, 1), 4),
                "ret_5m": round(random.uniform(-2, 2), 4),
                "ret_15m": round(random.uniform(-3, 3), 4),
                "ret_1h": round(random.uniform(-5, 5), 4),
                "ret_4h": round(random.uniform(-10, 10), 4),
                "ret_1d": round(random.uniform(-20, 20), 4),
                
                # Microstructure
                "liq_prints": random.randint(0, 20),
                "whale_flow": random.uniform(-1e7, 1e7),
                "funding_rate": round(random.uniform(-0.005, 0.005), 6),
                
                # Cross-market
                "btc_corr": round(random.uniform(0.3, 0.9), 2),
                "eth_corr": round(random.uniform(0.2, 0.8), 2),
                "fear_greed": random.randint(10, 90),
                
                # Categorical
                "exchange": random.choice(exchanges),
                "base_asset": random.choice(bases),
                "quote_asset": random.choice(quotes),
                "market_tier": random.choice(["TIER1", "TIER2", "TIER3"]),
                "sector": random.choice(sectors),
                "market_session": random.choice(["ASIA", "EUROPE", "US", "OVERNIGHT"]),
                
                # Text data
                "news_title": f"{random.choice(bases)} shows strong momentum amid market rally",
                "news_summary": f"Technical analysis suggests {random.choice(['bullish', 'bearish'])} outlook",
                "sentiment_text": random.choice(["positive market sentiment", "mixed signals", "bearish outlook"])
            }
            samples.append(sample)
        
        # Save as LDJSON
        crypto_file = self.test_data_path / "crypto_sample.ldjson"
        with open(crypto_file, 'w') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')
        
        print(f" Saved {count} crypto samples to {crypto_file}")
        return str(crypto_file)
    
    def test_basic_functions(self):
        """Test basic tokenizer functions"""
        print("\n Testing basic tokenizer functions...")
        
        # Test hash function
        hash1 = mmh("test_string")
        hash2 = mmh("test_string")
        assert hash1 == hash2, "Hash function not deterministic"
        print(" Hash function: deterministic")
        
        # Test normalization
        val = normalize_uint8(50, 0, 100)
        assert val == 127 or val == 128, f"Normalization failed: {val}"
        print(" Normalize function: correct scaling")
        
        # Test text sketch
        sketch1 = text_sketch("test message", slots=100)
        sketch2 = text_sketch("test message", slots=100)
        assert np.array_equal(sketch1, sketch2), "Text sketch not deterministic"
        assert sketch1.dtype == np.uint8, "Text sketch wrong dtype"
        assert len(sketch1) == 100, "Text sketch wrong length"
        print(" Text sketch: deterministic and correct shape")
    
    def test_sports_tokenization(self):
        """Test sports data tokenization"""
        print("\n Testing sports tokenization...")
        
        # Create test sample
        sample = {
            "moneyline": -150,
            "spread": -3.5,
            "total": 215.5,
            "implied_prob": 0.6,
            "team_home": "LAL",
            "team_away": "GSW",
            "market": "spread",
            "sportsbook": "draftkings",
            "headline": "Lakers injury report updated",
            "note": "Key player questionable"
        }
        
        # Tokenize
        tensor = self.tokenizer.sports(sample)
        
        # Validate
        assert tensor.dtype == np.uint8, f"Wrong dtype: {tensor.dtype}"
        assert len(tensor) == 256, f"Wrong length: {len(tensor)}"
        assert tensor.min() >= 0 and tensor.max() <= 255, "Values out of range"
        
        print(f" Sports tokenization: shape {tensor.shape}, dtype {tensor.dtype}")
        print(f"   Value range: [{tensor.min()}, {tensor.max()}]")
        print(f"   Non-zero features: {np.count_nonzero(tensor)}")
    
    def test_crypto_tokenization(self):
        """Test crypto data tokenization"""
        print("\n Testing crypto tokenization...")
        
        # Create test sample
        sample = {
            "price_usd": 42000,
            "volume_24h": 1e9,
            "rsi_14": 65,
            "ret_1m": 0.05,
            "exchange": "coinbase",
            "base_asset": "BTC",
            "quote_asset": "USD",
            "news_title": "Bitcoin rallies on institutional adoption"
        }
        
        # Tokenize
        tensor = self.tokenizer.crypto(sample)
        
        # Validate
        assert tensor.dtype == np.uint8, f"Wrong dtype: {tensor.dtype}"
        assert len(tensor) == 256, f"Wrong length: {len(tensor)}"
        assert tensor.min() >= 0 and tensor.max() <= 255, "Values out of range"
        
        print(f" Crypto tokenization: shape {tensor.shape}, dtype {tensor.dtype}")
        print(f"   Value range: [{tensor.min()}, {tensor.max()}]")
        print(f"   Non-zero features: {np.count_nonzero(tensor)}")
    
    def test_batch_processing(self):
        """Test batch tokenization performance"""
        print("\n Testing batch processing performance...")
        
        # Generate test data
        sports_file = self.generate_sports_sample(1000)
        crypto_file = self.generate_crypto_sample(1000)
        
        # Test sports batch processing
        start_time = time.time()
        
        # Load sports data
        sports_data = []
        with open(sports_file, 'r') as f:
            for line in f:
                sports_data.append(json.loads(line.strip()))
        
        # Batch tokenize
        sports_batch = self.tokenizer.batch_tokenize(sports_data, "sports")
        sports_time = time.time() - start_time
        
        print(f" Sports batch: {sports_batch.shape} in {sports_time:.2f}s")
        print(f"   Throughput: {len(sports_data)/sports_time:.0f} records/sec")
        
        # Test crypto batch processing
        start_time = time.time()
        
        # Load crypto data
        crypto_data = []
        with open(crypto_file, 'r') as f:
            for line in f:
                crypto_data.append(json.loads(line.strip()))
        
        # Batch tokenize
        crypto_batch = self.tokenizer.batch_tokenize(crypto_data, "crypto")
        crypto_time = time.time() - start_time
        
        print(f" Crypto batch: {crypto_batch.shape} in {crypto_time:.2f}s")
        print(f"   Throughput: {len(crypto_data)/crypto_time:.0f} records/sec")
        
        # Validate batches
        assert self.tokenizer.validate_output(sports_batch, "sports")
        assert self.tokenizer.validate_output(crypto_batch, "crypto")
        print(" Batch validation: all tensors valid")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n Testing edge cases...")
        
        # Empty data
        empty_tensor = self.tokenizer.sports({})
        assert len(empty_tensor) == 256, "Empty data handling failed"
        print(" Empty data: handled correctly")
        
        # Invalid numeric values
        invalid_sample = {
            "moneyline": "invalid",
            "spread": None,
            "total": float('inf'),
            "team_home": "",
            "sportsbook": None
        }
        
        invalid_tensor = self.tokenizer.sports(invalid_sample)
        assert len(invalid_tensor) == 256, "Invalid data handling failed"
        print(" Invalid data: handled with defaults")
        
        # Very long text
        long_text_sample = {
            "headline": "A" * 10000,  # Very long text
            "note": "B" * 5000
        }
        
        long_tensor = self.tokenizer.sports(long_text_sample)
        assert len(long_tensor) == 256, "Long text handling failed"
        print(" Long text: handled correctly")
    
    def run_full_test_suite(self):
        """Run complete test suite"""
        print(" EQ12 TOKENIZER TEST SUITE")
        print("=" * 50)
        
        try:
            self.test_basic_functions()
            self.test_sports_tokenization()
            self.test_crypto_tokenization()
            self.test_batch_processing()
            self.test_edge_cases()
            
            print("\n ALL TESTS PASSED!")
            print(" Tokenizer is production-ready for Coral TPU")
            
        except Exception as e:
            print(f"\n TEST FAILED: {e}")
            raise


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Tokenizer Test Suite")
    parser.add_argument("--workspace", default="C:/EQ12", help="Workspace path")
    parser.add_argument("--generate-only", action="store_true", help="Only generate sample data")
    parser.add_argument("--test-only", action="store_true", help="Only run tests")
    parser.add_argument("--sports-samples", type=int, default=100, help="Number of sports samples")
    parser.add_argument("--crypto-samples", type=int, default=100, help="Number of crypto samples")
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = TokenizerTestSuite(args.workspace)
    
    if args.generate_only:
        print(" Generating sample data only...")
        test_suite.generate_sports_sample(args.sports_samples)
        test_suite.generate_crypto_sample(args.crypto_samples)
        
    elif args.test_only:
        print(" Running tests only...")
        test_suite.run_full_test_suite()
        
    else:
        print(" Running full test suite with data generation...")
        test_suite.run_full_test_suite()


if __name__ == "__main__":
    main()