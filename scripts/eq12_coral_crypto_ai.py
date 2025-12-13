#!/usr/bin/env python3
"""
 EQ12 CORAL CRYPTO INTELLIGENCE CORE
Hardware-accelerated cryptocurrency analysis using Google Coral Edge TPU
Real-time price prediction, sentiment analysis, and trading signals
"""

import os
import sys
import json
import time
import logging
import asyncio
import websockets
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

# Coral Edge TPU imports
try:
    import tflite_runtime.interpreter as tflite
    from pycoral.utils import edgetpu
    from pycoral.adapters import common
    CORAL_AVAILABLE = True
except ImportError:
    print(" Coral TPU libraries not found - running in simulation mode")
    CORAL_AVAILABLE = False

# Crypto API clients
import ccxt
import pandas as pd
from scipy import stats


@dataclass 
class CryptoSignal:
    """Cryptocurrency trading signal from Coral TPU"""
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    ev_score: float
    price: float
    timestamp: datetime
    model_used: str
    features: Dict[str, float]


@dataclass
class MarketData:
    """Real-time market data structure"""
    symbol: str
    price: float
    volume: float
    change_24h: float
    volatility: float
    timestamp: datetime
    order_book: Dict[str, List]


class CoralCryptoAI:
    """
     Google Coral Edge TPU Crypto Intelligence Engine
    Real-time cryptocurrency analysis with hardware acceleration
    """
    
    def __init__(self, config_path: str = None):
        self.setup_logging()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize Coral TPU models
        self.models = {}
        self.coral_available = CORAL_AVAILABLE
        
        # Data feeds and exchanges
        self.exchanges = {}
        self.data_queue = queue.Queue(maxsize=10000)
        self.signal_queue = queue.Queue(maxsize=1000)
        
        # Performance metrics
        self.inference_times = []
        self.prediction_accuracy = []
        
        # Initialize systems
        self._initialize_exchanges()
        self._load_coral_models()
        
        self.logger.info(" EQ12 Coral Crypto AI initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        
        log_dir = "C:\\EQ12\\logs\\crypto"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"coral_crypto_ai_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load Coral Crypto AI configuration"""
        
        default_config = {
            "exchanges": {
                "binance": {
                    "enabled": True,
                    "symbols": ["BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "SOL/USDT"],
                    "api_key": "",
                    "api_secret": ""
                },
                "coinbase": {
                    "enabled": True,
                    "symbols": ["BTC/USD", "ETH/USD"],
                    "api_key": "",
                    "api_secret": ""
                }
            },
            "models": {
                "price_trend": "models/price_trend_lstm_edgetpu.tflite",
                "volatility_classifier": "models/volatility_classifier_edgetpu.tflite", 
                "sentiment_analyzer": "models/sentiment_microbert_edgetpu.tflite",
                "anomaly_detector": "models/anomaly_detector_edgetpu.tflite",
                "portfolio_optimizer": "models/portfolio_ev_edgetpu.tflite"
            },
            "alerts": {
                "telegram": {
                    "enabled": True,
                    "bot_token": "",
                    "chat_id": ""
                },
                "thresholds": {
                    "high_confidence": 0.85,
                    "medium_confidence": 0.70,
                    "ev_threshold": 0.60
                }
            },
            "features": {
                "technical_indicators": True,
                "sentiment_analysis": True,
                "order_book_analysis": True,
                "volatility_modeling": True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}, using defaults")
        
        return default_config
    
    def _initialize_exchanges(self):
        """Initialize cryptocurrency exchange connections"""
        
        self.logger.info(" Initializing crypto exchange connections...")
        
        for exchange_name, exchange_config in self.config["exchanges"].items():
            if not exchange_config.get("enabled", False):
                continue
                
            try:
                if exchange_name == "binance":
                    exchange = ccxt.binance({
                        'apiKey': exchange_config.get("api_key", ""),
                        'secret': exchange_config.get("api_secret", ""),
                        'sandbox': True,  # Use testnet for safety
                        'enableRateLimit': True
                    })
                elif exchange_name == "coinbase":
                    exchange = ccxt.coinbasepro({
                        'apiKey': exchange_config.get("api_key", ""),
                        'secret': exchange_config.get("api_secret", ""),
                        'enableRateLimit': True
                    })
                else:
                    continue
                
                # Test connection
                exchange.load_markets()
                self.exchanges[exchange_name] = exchange
                
                self.logger.info(f" Connected to {exchange_name}")
                
            except Exception as e:
                self.logger.error(f" Failed to connect to {exchange_name}: {e}")
    
    def _load_coral_models(self):
        """Load and initialize Coral Edge TPU models"""
        
        self.logger.info(" Loading Coral Edge TPU models...")
        
        if not self.coral_available:
            self.logger.warning(" Coral TPU not available - using CPU simulation")
            return
        
        model_configs = self.config.get("models", {})
        
        for model_name, model_path in model_configs.items():
            try:
                if os.path.exists(model_path):
                    # Initialize Edge TPU interpreter
                    interpreter = tflite.Interpreter(
                        model_path=model_path,
                        experimental_delegates=[edgetpu.make_interpreter()]
                    )
                    interpreter.allocate_tensors()
                    
                    self.models[model_name] = {
                        'interpreter': interpreter,
                        'input_details': interpreter.get_input_details(),
                        'output_details': interpreter.get_output_details(),
                        'path': model_path
                    }
                    
                    self.logger.info(f" Loaded Coral model: {model_name}")
                    
                else:
                    # Create placeholder model for development
                    self.models[model_name] = {
                        'interpreter': None,
                        'input_details': [{'shape': [1, 60, 5]}],  # Mock OHLCV input
                        'output_details': [{'shape': [1, 3]}],     # Mock 3-class output
                        'path': model_path,
                        'simulated': True
                    }
                    
                    self.logger.warning(f" Model not found, using simulation: {model_name}")
                    
            except Exception as e:
                self.logger.error(f" Failed to load model {model_name}: {e}")
    
    def run_coral_inference(self, model_name: str, input_data: np.ndarray) -> np.ndarray:
        """
         Run inference on Coral Edge TPU
        Ultra-fast hardware-accelerated prediction
        """
        
        if model_name not in self.models:
            self.logger.error(f"Model not found: {model_name}")
            return np.array([0.33, 0.33, 0.34])  # Neutral prediction
        
        model = self.models[model_name]
        
        # Start timing
        start_time = time.time()
        
        try:
            if model.get('simulated', False) or not self.coral_available:
                # Simulation mode for development
                inference_result = self._simulate_model_inference(model_name, input_data)
            else:
                # Real Coral TPU inference
                interpreter = model['interpreter']
                input_details = model['input_details'][0]
                output_details = model['output_details'][0]
                
                # Set input tensor
                interpreter.set_tensor(input_details['index'], input_data.astype(np.float32))
                
                # Run inference on Edge TPU
                interpreter.invoke()
                
                # Get output
                inference_result = interpreter.get_tensor(output_details['index'])
            
            # Record performance
            inference_time = time.time() - start_time
            self.inference_times.append(inference_time)
            
            # Keep only recent performance data
            if len(self.inference_times) > 1000:
                self.inference_times = self.inference_times[-1000:]
            
            self.logger.debug(f" Coral inference ({model_name}): {inference_time*1000:.2f}ms")
            
            return inference_result.flatten()
            
        except Exception as e:
            self.logger.error(f" Coral inference failed ({model_name}): {e}")
            return np.array([0.33, 0.33, 0.34])  # Safe fallback
    
    def _simulate_model_inference(self, model_name: str, input_data: np.ndarray) -> np.ndarray:
        """Simulate model inference for development/testing"""
        
        # Add small delay to simulate TPU processing
        time.sleep(0.001)
        
        if model_name == "price_trend":
            # Simulate price direction prediction: [down, neutral, up]
            trend = np.random.dirichlet([1, 2, 1])  # Slight bias toward neutral
            return trend.reshape(1, -1)
            
        elif model_name == "volatility_classifier":
            # Simulate volatility classification: [low, medium, high]
            vol = np.random.dirichlet([2, 3, 1])  # Bias toward low-medium vol
            return vol.reshape(1, -1)
            
        elif model_name == "sentiment_analyzer":
            # Simulate sentiment score: single value 0-1
            sentiment = np.random.beta(2, 2)  # Bell curve around 0.5
            return np.array([[sentiment]])
            
        elif model_name == "anomaly_detector":
            # Simulate anomaly detection: binary classification
            anomaly = np.random.choice([0, 1], p=[0.95, 0.05])  # 5% anomaly rate
            return np.array([[anomaly]])
            
        elif model_name == "portfolio_optimizer":
            # Simulate EV score: single value 0-1
            ev_score = np.random.beta(3, 2)  # Slight positive bias
            return np.array([[ev_score]])
        
        else:
            # Default neutral prediction
            return np.array([[0.5]])
    
    async def collect_market_data(self, symbol: str, exchange_name: str = "binance") -> MarketData:
        """Collect real-time market data for analysis"""
        
        if exchange_name not in self.exchanges:
            self.logger.error(f"Exchange not available: {exchange_name}")
            return None
        
        exchange = self.exchanges[exchange_name]
        
        try:
            # Get ticker data
            ticker = exchange.fetch_ticker(symbol)
            
            # Get order book
            order_book = exchange.fetch_order_book(symbol, limit=20)
            
            # Calculate additional metrics
            volatility = self._calculate_volatility(symbol, exchange)
            
            market_data = MarketData(
                symbol=symbol,
                price=ticker['last'],
                volume=ticker['baseVolume'],
                change_24h=ticker['percentage'],
                volatility=volatility,
                timestamp=datetime.now(),
                order_book=order_book
            )
            
            return market_data
            
        except Exception as e:
            self.logger.error(f" Failed to collect market data for {symbol}: {e}")
            return None
    
    def _calculate_volatility(self, symbol: str, exchange, periods: int = 24) -> float:
        """Calculate recent volatility for risk assessment"""
        
        try:
            # Get recent OHLCV data
            ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=periods)
            closes = [candle[4] for candle in ohlcv]  # Close prices
            
            # Calculate returns
            returns = np.diff(np.log(closes))
            
            # Return annualized volatility
            return np.std(returns) * np.sqrt(365 * 24)
            
        except Exception as e:
            self.logger.error(f"Volatility calculation failed: {e}")
            return 0.0
    
    def analyze_crypto_signal(self, market_data: MarketData) -> CryptoSignal:
        """
         Complete crypto signal analysis using Coral TPU
        Combines price prediction, volatility, sentiment, and EV calculation
        """
        
        try:
            # Prepare features for model input
            features = self._extract_features(market_data)
            
            # 1. Price trend prediction (Coral TPU)
            trend_input = self._prepare_price_trend_input(features)
            trend_prediction = self.run_coral_inference("price_trend", trend_input)
            
            # 2. Volatility classification (Coral TPU)
            vol_input = self._prepare_volatility_input(features)
            vol_prediction = self.run_coral_inference("volatility_classifier", vol_input)
            
            # 3. Portfolio EV scoring (Coral TPU)
            ev_input = self._prepare_ev_input(features)
            ev_prediction = self.run_coral_inference("portfolio_optimizer", ev_input)
            
            # 4. Anomaly detection (Coral TPU)
            anomaly_input = self._prepare_anomaly_input(features)
            anomaly_prediction = self.run_coral_inference("anomaly_detector", anomaly_input)
            
            # Combine predictions into trading signal
            signal = self._generate_trading_signal(
                trend_prediction, vol_prediction, ev_prediction, 
                anomaly_prediction, market_data, features
            )
            
            return signal
            
        except Exception as e:
            self.logger.error(f" Signal analysis failed for {market_data.symbol}: {e}")
            
            # Return neutral signal on error
            return CryptoSignal(
                symbol=market_data.symbol,
                signal_type='HOLD',
                confidence=0.0,
                ev_score=0.0,
                price=market_data.price,
                timestamp=datetime.now(),
                model_used='error_fallback',
                features={}
            )
    
    def _extract_features(self, market_data: MarketData) -> Dict[str, float]:
        """Extract technical and market features"""
        
        features = {
            'price': market_data.price,
            'volume': market_data.volume,
            'change_24h': market_data.change_24h,
            'volatility': market_data.volatility,
            'bid_ask_spread': 0.0,
            'order_book_imbalance': 0.0,
            'volume_weighted_price': market_data.price
        }
        
        # Calculate order book features
        if market_data.order_book:
            try:
                bids = market_data.order_book.get('bids', [])
                asks = market_data.order_book.get('asks', [])
                
                if bids and asks:
                    best_bid = bids[0][0]
                    best_ask = asks[0][0]
                    
                    features['bid_ask_spread'] = (best_ask - best_bid) / best_bid
                    
                    # Order book imbalance
                    bid_volume = sum([bid[1] for bid in bids[:10]])
                    ask_volume = sum([ask[1] for ask in asks[:10]])
                    total_volume = bid_volume + ask_volume
                    
                    if total_volume > 0:
                        features['order_book_imbalance'] = (bid_volume - ask_volume) / total_volume
                        
            except Exception as e:
                self.logger.debug(f"Order book feature extraction failed: {e}")
        
        return features
    
    def _prepare_price_trend_input(self, features: Dict[str, float]) -> np.ndarray:
        """Prepare input for price trend LSTM model"""
        
        # Mock time series data (in production, use actual historical data)
        sequence_length = 60
        feature_count = 5  # OHLCV
        
        # Create mock sequence with current features
        mock_sequence = np.random.randn(1, sequence_length, feature_count)
        
        # Inject current market state into last timestep
        mock_sequence[0, -1, 0] = features.get('price', 0) / 50000  # Normalized price
        mock_sequence[0, -1, 1] = features.get('volume', 0) / 1000  # Normalized volume
        mock_sequence[0, -1, 2] = features.get('volatility', 0)
        mock_sequence[0, -1, 3] = features.get('change_24h', 0) / 100
        mock_sequence[0, -1, 4] = features.get('bid_ask_spread', 0) * 1000
        
        return mock_sequence.astype(np.float32)
    
    def _prepare_volatility_input(self, features: Dict[str, float]) -> np.ndarray:
        """Prepare input for volatility classifier"""
        
        vol_features = np.array([[
            features.get('volatility', 0),
            features.get('change_24h', 0) / 100,
            features.get('volume', 0) / 1000,
            features.get('bid_ask_spread', 0) * 1000,
            features.get('order_book_imbalance', 0)
        ]])
        
        return vol_features.astype(np.float32)
    
    def _prepare_ev_input(self, features: Dict[str, float]) -> np.ndarray:
        """Prepare input for EV/portfolio optimizer"""
        
        ev_features = np.array([[
            features.get('change_24h', 0) / 100,
            features.get('volatility', 0),
            features.get('order_book_imbalance', 0),
            abs(features.get('change_24h', 0)) / 100,  # Momentum
            features.get('volume', 0) / 1000
        ]])
        
        return ev_features.astype(np.float32)
    
    def _prepare_anomaly_input(self, features: Dict[str, float]) -> np.ndarray:
        """Prepare input for anomaly detector"""
        
        anomaly_features = np.array([[
            features.get('bid_ask_spread', 0) * 1000,
            abs(features.get('order_book_imbalance', 0)),
            features.get('volatility', 0),
            abs(features.get('change_24h', 0)) / 100,
            features.get('volume', 0) / 1000
        ]])
        
        return anomaly_features.astype(np.float32)
    
    def _generate_trading_signal(self, trend_pred: np.ndarray, vol_pred: np.ndarray, 
                               ev_pred: np.ndarray, anomaly_pred: np.ndarray,
                               market_data: MarketData, features: Dict[str, float]) -> CryptoSignal:
        """Generate final trading signal from Coral TPU predictions"""
        
        # Extract predictions
        trend_probs = trend_pred  # [down, neutral, up]
        vol_class = np.argmax(vol_pred)  # 0=low, 1=med, 2=high
        ev_score = float(ev_pred[0])
        is_anomaly = anomaly_pred[0] > 0.5
        
        # Determine signal type
        up_prob = trend_probs[2] if len(trend_probs) >= 3 else 0.33
        down_prob = trend_probs[0] if len(trend_probs) >= 3 else 0.33
        
        # Risk adjustment based on volatility
        vol_multiplier = [1.2, 1.0, 0.7][vol_class]  # Reduce confidence in high vol
        
        # Anomaly penalty
        anomaly_penalty = 0.5 if is_anomaly else 1.0
        
        # Calculate final confidence
        raw_confidence = max(up_prob, down_prob)
        adjusted_confidence = raw_confidence * vol_multiplier * anomaly_penalty
        
        # Determine signal
        if adjusted_confidence > 0.7 and up_prob > down_prob and ev_score > 0.6:
            signal_type = 'BUY'
        elif adjusted_confidence > 0.7 and down_prob > up_prob and ev_score > 0.6:
            signal_type = 'SELL'
        else:
            signal_type = 'HOLD'
        
        return CryptoSignal(
            symbol=market_data.symbol,
            signal_type=signal_type,
            confidence=float(adjusted_confidence),
            ev_score=ev_score,
            price=market_data.price,
            timestamp=datetime.now(),
            model_used='coral_ensemble',
            features={
                'trend_up_prob': float(up_prob),
                'trend_down_prob': float(down_prob),
                'volatility_class': int(vol_class),
                'is_anomaly': bool(is_anomaly),
                'ev_score': float(ev_score),
                'confidence_raw': float(raw_confidence),
                'confidence_adjusted': float(adjusted_confidence)
            }
        )
    
    async def send_alert(self, signal: CryptoSignal):
        """Send trading signal alert via Telegram"""
        
        if not self.config.get("alerts", {}).get("telegram", {}).get("enabled", False):
            return
        
        try:
            bot_token = self.config["alerts"]["telegram"]["bot_token"]
            chat_id = self.config["alerts"]["telegram"]["chat_id"]
            
            if not bot_token or not chat_id:
                self.logger.warning("Telegram credentials not configured")
                return
            
            # Format alert message
            alert_message = self._format_alert_message(signal)
            
            # Send via Telegram API
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': alert_message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(f" Alert sent for {signal.symbol}")
            else:
                self.logger.error(f" Failed to send alert: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f" Alert sending failed: {e}")
    
    def _format_alert_message(self, signal: CryptoSignal) -> str:
        """Format trading signal for alert message"""
        
        emoji_map = {'BUY': '', 'SELL': '', 'HOLD': ''}
        emoji = emoji_map.get(signal.signal_type, '')
        
        message = f"""
 <b>EQ12 Coral Crypto Signal</b>

{emoji} <b>{signal.signal_type}</b> - {signal.symbol}
 Price: ${signal.price:,.2f}
 Confidence: {signal.confidence:.1%}
 EV Score: {signal.ev_score:.1%}
 Model: {signal.model_used}

 Processed by Google Coral Edge TPU
 {signal.timestamp.strftime('%H:%M:%S')}
        """.strip()
        
        return message
    
    def save_signal_log(self, signal: CryptoSignal):
        """Save trading signal to log file"""
        
        log_dir = "C:\\EQ12\\logs\\crypto\\signals"
        os.makedirs(log_dir, exist_ok=True)
        
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"crypto_signals_{date_str}.json")
        
        signal_data = {
            'timestamp': signal.timestamp.isoformat(),
            'symbol': signal.symbol,
            'signal_type': signal.signal_type,
            'confidence': signal.confidence,
            'ev_score': signal.ev_score,
            'price': signal.price,
            'model_used': signal.model_used,
            'features': signal.features
        }
        
        try:
            # Append to daily log file
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(signal_data)
            
            # Keep only recent signals (max 10000 per day)
            if len(logs) > 10000:
                logs = logs[-10000:]
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            self.logger.error(f" Failed to save signal log: {e}")
    
    async def run_continuous_analysis(self):
        """
         Continuous crypto analysis loop
        Processes multiple symbols in parallel using Coral TPU
        """
        
        self.logger.info(" Starting continuous crypto analysis...")
        
        # Get all configured symbols
        all_symbols = []
        for exchange_name, exchange_config in self.config["exchanges"].items():
            if exchange_config.get("enabled", False):
                symbols = exchange_config.get("symbols", [])
                for symbol in symbols:
                    all_symbols.append((symbol, exchange_name))
        
        if not all_symbols:
            self.logger.error(" No symbols configured for analysis")
            return
        
        self.logger.info(f" Analyzing {len(all_symbols)} symbols: {[s[0] for s in all_symbols]}")
        
        while True:
            try:
                # Process all symbols in parallel
                tasks = []
                for symbol, exchange_name in all_symbols:
                    task = self._analyze_single_symbol(symbol, exchange_name)
                    tasks.append(task)
                
                # Execute all analyses concurrently
                signals = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                valid_signals = []
                for signal in signals:
                    if isinstance(signal, CryptoSignal):
                        valid_signals.append(signal)
                        
                        # Save signal
                        self.save_signal_log(signal)
                        
                        # Send alerts for high-confidence signals
                        confidence_threshold = self.config.get("alerts", {}).get("thresholds", {}).get("high_confidence", 0.85)
                        if signal.confidence >= confidence_threshold:
                            await self.send_alert(signal)
                
                # Log analysis summary
                self.logger.info(f" Analyzed {len(valid_signals)} symbols, "
                               f"avg inference time: {np.mean(self.inference_times[-100:]) * 1000:.1f}ms")
                
                # Wait before next analysis cycle
                await asyncio.sleep(30)  # 30-second intervals
                
            except Exception as e:
                self.logger.error(f" Analysis cycle failed: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _analyze_single_symbol(self, symbol: str, exchange_name: str) -> CryptoSignal:
        """Analyze a single cryptocurrency symbol"""
        
        try:
            # Collect market data
            market_data = await self.collect_market_data(symbol, exchange_name)
            
            if market_data is None:
                return None
            
            # Run Coral TPU analysis
            signal = self.analyze_crypto_signal(market_data)
            
            return signal
            
        except Exception as e:
            self.logger.error(f" Failed to analyze {symbol}: {e}")
            return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get Coral TPU performance statistics"""
        
        if not self.inference_times:
            return {"status": "No inference data available"}
        
        recent_times = self.inference_times[-100:]  # Last 100 inferences
        
        return {
            "avg_inference_time_ms": np.mean(recent_times) * 1000,
            "min_inference_time_ms": np.min(recent_times) * 1000,
            "max_inference_time_ms": np.max(recent_times) * 1000,
            "total_inferences": len(self.inference_times),
            "coral_available": self.coral_available,
            "models_loaded": len(self.models),
            "exchanges_connected": len(self.exchanges)
        }


async def main():
    """Main function to run EQ12 Coral Crypto AI"""
    
    print(" Starting EQ12 Coral Crypto Intelligence System...")
    
    # Initialize the AI system
    crypto_ai = CoralCryptoAI()
    
    # Display system status
    print("\n" + "="*70)
    print(" EQ12 CORAL CRYPTO AI - SYSTEM STATUS")
    print("="*70)
    
    performance = crypto_ai.get_performance_stats()
    print(f" Coral TPU Available: {'' if performance.get('coral_available') else ''}")
    print(f" Models Loaded: {performance.get('models_loaded', 0)}")
    print(f" Exchanges Connected: {performance.get('exchanges_connected', 0)}")
    
    if crypto_ai.exchanges:
        print(f" Active Exchanges: {', '.join(crypto_ai.exchanges.keys())}")
    
    print("="*70)
    
    # Start continuous analysis
    try:
        await crypto_ai.run_continuous_analysis()
    except KeyboardInterrupt:
        print("\n Analysis stopped by user")
    except Exception as e:
        print(f"\n System error: {e}")


if __name__ == "__main__":
    asyncio.run(main())