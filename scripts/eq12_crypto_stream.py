#!/usr/bin/env python3
"""
 EQ12 CRYPTO DATA STREAM COLLECTOR
Real-time cryptocurrency data collection from multiple exchanges
Feeds live data to Coral TPU analysis engine
"""

import os
import json
import time
import logging
import asyncio
import websockets
import requests
from datetime import datetime
from typing import Dict, List, Any
import ccxt


class CryptoDataStreamer:
    """
     Real-time cryptocurrency data streaming service
    Collects live price feeds for Coral TPU analysis
    """
    
    def __init__(self, config_path: str = None):
        self.setup_logging()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize exchanges
        self.exchanges = {}
        self.active_streams = {}
        
        # Data storage
        self.data_buffer = {}
        self.feed_directory = "C:\\EQ12\\feeds\\crypto"
        
        # Initialize systems
        self._initialize_exchanges()
        self._setup_feed_directory()
        
        self.logger.info(" EQ12 Crypto Data Streamer initialized")
    
    def setup_logging(self):
        """Setup logging system"""
        
        log_dir = "C:\\EQ12\\logs\\crypto"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"crypto_stream_{timestamp}.log")
        
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
        """Load streaming configuration"""
        
        default_config = {
            "exchanges": {
                "binance": {
                    "enabled": True,
                    "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"],
                    "streams": ["ticker", "trade", "depth"]
                },
                "coinbase": {
                    "enabled": True,
                    "symbols": ["BTC-USD", "ETH-USD"],
                    "streams": ["ticker", "matches"]
                }
            },
            "feed_settings": {
                "buffer_size": 1000,
                "save_interval": 60,
                "compress_data": True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _initialize_exchanges(self):
        """Initialize exchange connections"""
        
        for exchange_name, exchange_config in self.config["exchanges"].items():
            if not exchange_config.get("enabled", False):
                continue
                
            try:
                if exchange_name == "binance":
                    exchange = ccxt.binance({
                        'enableRateLimit': True,
                        'sandbox': True
                    })
                elif exchange_name == "coinbase":
                    exchange = ccxt.coinbasepro({
                        'enableRateLimit': True
                    })
                else:
                    continue
                
                exchange.load_markets()
                self.exchanges[exchange_name] = exchange
                
                self.logger.info(f" Initialized {exchange_name}")
                
            except Exception as e:
                self.logger.error(f" Failed to initialize {exchange_name}: {e}")
    
    def _setup_feed_directory(self):
        """Setup feed storage directory"""
        
        os.makedirs(self.feed_directory, exist_ok=True)
        
        # Create subdirectories
        subdirs = ["raw", "processed", "archive"]
        for subdir in subdirs:
            os.makedirs(os.path.join(self.feed_directory, subdir), exist_ok=True)
    
    async def start_binance_stream(self, symbols: List[str]):
        """Start Binance WebSocket stream"""
        
        if not symbols:
            return
        
        # Format symbols for Binance WebSocket
        stream_symbols = [symbol.lower() for symbol in symbols]
        
        # Create stream URLs
        streams = []
        for symbol in stream_symbols:
            streams.extend([
                f"{symbol}@ticker",
                f"{symbol}@trade",
                f"{symbol}@depth20@100ms"
            ])
        
        stream_url = f"wss://stream.binance.com:9443/ws/{'/'.join(streams)}"
        
        try:
            self.logger.info(f" Connecting to Binance stream: {len(symbols)} symbols")
            
            async with websockets.connect(stream_url) as websocket:
                self.active_streams["binance"] = websocket
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self._process_binance_message(data)
                        
                    except Exception as e:
                        self.logger.error(f"Binance message processing error: {e}")
                        
        except Exception as e:
            self.logger.error(f" Binance stream error: {e}")
    
    async def _process_binance_message(self, data: Dict[str, Any]):
        """Process incoming Binance WebSocket message"""
        
        try:
            stream_type = data.get("stream", "").split("@")[-1].split("@")[0]
            
            if stream_type == "ticker":
                await self._handle_ticker_data("binance", data["data"])
            elif stream_type == "trade":
                await self._handle_trade_data("binance", data["data"])
            elif stream_type.startswith("depth"):
                await self._handle_depth_data("binance", data["data"])
                
        except Exception as e:
            self.logger.error(f"Binance message handling error: {e}")
    
    async def _handle_ticker_data(self, exchange: str, data: Dict[str, Any]):
        """Handle ticker/price data"""
        
        symbol = data.get("s") if exchange == "binance" else data.get("product_id")
        
        ticker_data = {
            "exchange": exchange,
            "symbol": symbol,
            "price": float(data.get("c", 0)) if exchange == "binance" else float(data.get("price", 0)),
            "volume": float(data.get("v", 0)) if exchange == "binance" else float(data.get("volume_24h", 0)),
            "change": float(data.get("P", 0)) if exchange == "binance" else 0,
            "timestamp": datetime.now().isoformat(),
            "type": "ticker"
        }
        
        # Store in buffer
        await self._store_data(ticker_data)
        
        # Save to feed file
        await self._save_ticker_feed(ticker_data)
    
    async def _handle_trade_data(self, exchange: str, data: Dict[str, Any]):
        """Handle trade execution data"""
        
        symbol = data.get("s") if exchange == "binance" else data.get("product_id")
        
        trade_data = {
            "exchange": exchange,
            "symbol": symbol,
            "price": float(data.get("p", 0)) if exchange == "binance" else float(data.get("price", 0)),
            "quantity": float(data.get("q", 0)) if exchange == "binance" else float(data.get("size", 0)),
            "side": "buy" if data.get("m", True) else "sell",
            "timestamp": datetime.now().isoformat(),
            "type": "trade"
        }
        
        await self._store_data(trade_data)
    
    async def _handle_depth_data(self, exchange: str, data: Dict[str, Any]):
        """Handle order book depth data"""
        
        symbol = data.get("s")
        
        depth_data = {
            "exchange": exchange,
            "symbol": symbol,
            "bids": data.get("bids", [])[:10],  # Top 10 bids
            "asks": data.get("asks", [])[:10],  # Top 10 asks
            "timestamp": datetime.now().isoformat(),
            "type": "depth"
        }
        
        await self._store_data(depth_data)
    
    async def _store_data(self, data: Dict[str, Any]):
        """Store data in memory buffer"""
        
        symbol = data["symbol"]
        
        if symbol not in self.data_buffer:
            self.data_buffer[symbol] = []
        
        self.data_buffer[symbol].append(data)
        
        # Limit buffer size
        max_buffer = self.config.get("feed_settings", {}).get("buffer_size", 1000)
        if len(self.data_buffer[symbol]) > max_buffer:
            self.data_buffer[symbol] = self.data_buffer[symbol][-max_buffer:]
    
    async def _save_ticker_feed(self, ticker_data: Dict[str, Any]):
        """Save ticker data to feed file for Coral AI consumption"""
        
        symbol = ticker_data["symbol"]
        date_str = datetime.now().strftime("%Y%m%d")
        
        feed_file = os.path.join(
            self.feed_directory, "raw", 
            f"{ticker_data['exchange']}_{symbol}_{date_str}.json"
        )
        
        try:
            # Load existing data
            if os.path.exists(feed_file):
                with open(feed_file, 'r') as f:
                    feed_data = json.load(f)
            else:
                feed_data = []
            
            # Append new data
            feed_data.append(ticker_data)
            
            # Keep only recent data (last 10000 records)
            if len(feed_data) > 10000:
                feed_data = feed_data[-10000:]
            
            # Save updated data
            with open(feed_file, 'w') as f:
                json.dump(feed_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save feed data: {e}")
    
    async def collect_exchange_data(self, exchange_name: str, symbols: List[str]):
        """Collect data from exchange REST API"""
        
        if exchange_name not in self.exchanges:
            return
        
        exchange = self.exchanges[exchange_name]
        
        for symbol in symbols:
            try:
                # Get ticker
                ticker = exchange.fetch_ticker(symbol)
                
                ticker_data = {
                    "exchange": exchange_name,
                    "symbol": symbol,
                    "price": ticker["last"],
                    "volume": ticker["baseVolume"],
                    "change": ticker["percentage"],
                    "timestamp": datetime.now().isoformat(),
                    "type": "ticker",
                    "source": "rest_api"
                }
                
                await self._store_data(ticker_data)
                await self._save_ticker_feed(ticker_data)
                
            except Exception as e:
                self.logger.error(f"Failed to collect {symbol} from {exchange_name}: {e}")
    
    def get_latest_data(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get latest data for a symbol"""
        
        if symbol not in self.data_buffer:
            return []
        
        return self.data_buffer[symbol][-limit:]
    
    def get_feed_status(self) -> Dict[str, Any]:
        """Get streaming feed status"""
        
        return {
            "active_streams": len(self.active_streams),
            "buffered_symbols": len(self.data_buffer),
            "total_data_points": sum(len(data) for data in self.data_buffer.values()),
            "exchanges_connected": len(self.exchanges),
            "feed_directory": self.feed_directory
        }
    
    async def run_streaming(self):
        """Run the data streaming service"""
        
        self.logger.info(" Starting crypto data streaming...")
        
        tasks = []
        
        # Start WebSocket streams
        for exchange_name, exchange_config in self.config["exchanges"].items():
            if not exchange_config.get("enabled", False):
                continue
            
            symbols = exchange_config.get("symbols", [])
            
            if exchange_name == "binance" and symbols:
                task = asyncio.create_task(self.start_binance_stream(symbols))
                tasks.append(task)
        
        # Start REST API polling
        async def rest_polling():
            while True:
                for exchange_name, exchange_config in self.config["exchanges"].items():
                    if exchange_config.get("enabled", False):
                        symbols = exchange_config.get("symbols", [])
                        await self.collect_exchange_data(exchange_name, symbols)
                
                await asyncio.sleep(30)  # Poll every 30 seconds
        
        rest_task = asyncio.create_task(rest_polling())
        tasks.append(rest_task)
        
        # Run all tasks
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")


async def main():
    """Main streaming function"""
    
    print(" Starting EQ12 Crypto Data Streaming Service...")
    
    streamer = CryptoDataStreamer()
    
    # Display status
    status = streamer.get_feed_status()
    print(f" Exchanges: {status['exchanges_connected']}")
    print(f" Symbols: {status['buffered_symbols']}")
    print(f" Feed Directory: {status['feed_directory']}")
    
    try:
        await streamer.run_streaming()
    except KeyboardInterrupt:
        print("\n Streaming stopped by user")


if __name__ == "__main__":
    asyncio.run(main())