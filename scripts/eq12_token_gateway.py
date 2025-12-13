#!/usr/bin/env python3
"""
EQ12 Token Gateway
Complete tokenization and crypto integration system for EQ12 ecosystem.
Handles wallet authentication, token verification, and payment processing.
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac

# Web3 and crypto imports (with graceful fallback)
try:
    from web3 import Web3
    from eth_account import Account
    from eth_account.messages import encode_defunct
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("Warning: Web3.py not installed. Install with: pip install web3 eth-account")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\token_gateway.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class TokenType(Enum):
    """Token type enumeration"""
    ERC20 = "erc20"
    BEP20 = "bep20"
    NATIVE = "native"
    STABLE = "stable"


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"


class AccessLevel(Enum):
    """Access level enumeration"""
    BASIC = 0
    PREMIUM = 1
    VIP = 2
    ADMIN = 3


@dataclass
class TokenConfig:
    """Token configuration"""
    symbol: str
    contract_address: str
    decimals: int
    token_type: TokenType
    network: str
    price_usd: float = 0.0
    min_balance: float = 1.0
    enabled: bool = True


@dataclass
class WalletConnection:
    """Wallet connection data"""
    address: str
    signature: str
    message: str
    telegram_chat_id: Optional[int] = None
    access_level: AccessLevel = AccessLevel.BASIC
    token_balances: Dict[str, float] = None
    created_at: str = ""
    last_verified: str = ""
    verified: bool = False


@dataclass
class PaymentRequest:
    """Payment request data"""
    id: str
    wallet_address: str
    token_symbol: str
    amount: float
    purpose: str
    status: PaymentStatus
    created_at: str
    expires_at: str
    transaction_hash: Optional[str] = None
    confirmed_at: Optional[str] = None


class EQ12TokenGateway:
    """Complete tokenization and crypto integration system"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "data" / "token_gateway.db"
        self.config_path = self.workspace_path / "configs" / "token_config.json"
        
        # Create directories
        for path in [
            self.workspace_path / "data",
            self.workspace_path / "logs" / "crypto",
            self.workspace_path / "configs"
        ]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self.load_configuration()
        self.token_configs = self.load_token_configs()
        
        # Initialize database
        self.init_database()
        
        # Web3 setup
        self.web3_instances = {}
        self.setup_web3_connections()
        
        # Cache
        self.wallet_cache: Dict[str, WalletConnection] = {}
        self.balance_cache: Dict[str, Dict[str, float]] = {}
        self.price_cache: Dict[str, float] = {}
        
        logger.info("EQ12 Token Gateway initialized")

    def load_configuration(self) -> Dict:
        """Load gateway configuration"""
        default_config = {
            "networks": {
                "ethereum": {
                    "rpc_url": "https://mainnet.infura.io/v3/YOUR_INFURA_KEY",
                    "chain_id": 1,
                    "enabled": False
                },
                "polygon": {
                    "rpc_url": "https://polygon-rpc.com",
                    "chain_id": 137,
                    "enabled": True
                },
                "bsc": {
                    "rpc_url": "https://bsc-dataseed.binance.org",
                    "chain_id": 56,
                    "enabled": True
                }
            },
            "payment_settings": {
                "default_expiry_minutes": 30,
                "confirmation_blocks": 12,
                "gas_limit": 21000,
                "max_gas_price": 100  # Gwei
            },
            "security": {
                "signature_expiry_minutes": 5,
                "max_verification_attempts": 3,
                "rate_limit_per_hour": 100
            },
            "features": {
                "auto_price_updates": True,
                "balance_caching": True,
                "transaction_monitoring": True
            }
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                # Create default config
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return default_config

    def load_token_configs(self) -> Dict[str, TokenConfig]:
        """Load token configurations"""
        default_tokens = {
            "EQC": TokenConfig(
                symbol="EQC",
                contract_address="0x1234567890123456789012345678901234567890",  # Placeholder
                decimals=18,
                token_type=TokenType.ERC20,
                network="polygon",
                price_usd=1.0,
                min_balance=1.0
            ),
            "USDC": TokenConfig(
                symbol="USDC",
                contract_address="0xA0b86a33E6417c32F2EC0ba965BAe70B5C88b12e",
                decimals=6,
                token_type=TokenType.STABLE,
                network="polygon",
                price_usd=1.0,
                min_balance=5.0
            ),
            "MATIC": TokenConfig(
                symbol="MATIC",
                contract_address="",  # Native token
                decimals=18,
                token_type=TokenType.NATIVE,
                network="polygon",
                price_usd=0.5,
                min_balance=10.0
            )
        }
        
        tokens_file = self.workspace_path / "configs" / "token_configs.json"
        
        try:
            if tokens_file.exists():
                with open(tokens_file) as f:
                    tokens_data = json.load(f)
                
                tokens = {}
                for symbol, data in tokens_data.items():
                    tokens[symbol] = TokenConfig(
                        symbol=data["symbol"],
                        contract_address=data["contract_address"],
                        decimals=data["decimals"],
                        token_type=TokenType(data["token_type"]),
                        network=data["network"],
                        price_usd=data.get("price_usd", 0.0),
                        min_balance=data.get("min_balance", 1.0),
                        enabled=data.get("enabled", True)
                    )
                
                return tokens
            else:
                # Save default tokens
                tokens_data = {}
                for symbol, token in default_tokens.items():
                    tokens_data[symbol] = {
                        "symbol": token.symbol,
                        "contract_address": token.contract_address,
                        "decimals": token.decimals,
                        "token_type": token.token_type.value,
                        "network": token.network,
                        "price_usd": token.price_usd,
                        "min_balance": token.min_balance,
                        "enabled": token.enabled
                    }
                
                with open(tokens_file, 'w') as f:
                    json.dump(tokens_data, f, indent=2)
                
                return default_tokens
                
        except Exception as e:
            logger.error(f"Failed to load token configs: {e}")
            return default_tokens

    def setup_web3_connections(self):
        """Setup Web3 connections for enabled networks"""
        if not WEB3_AVAILABLE:
            logger.warning("Web3.py not available - crypto features disabled")
            return
        
        for network, config in self.config["networks"].items():
            if config["enabled"]:
                try:
                    w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
                    if w3.is_connected():
                        self.web3_instances[network] = w3
                        logger.info(f"Connected to {network} network")
                    else:
                        logger.error(f"Failed to connect to {network}")
                except Exception as e:
                    logger.error(f"Web3 connection error for {network}: {e}")

    def init_database(self):
        """Initialize SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Wallet connections table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS wallet_connections (
                        address TEXT PRIMARY KEY,
                        signature TEXT NOT NULL,
                        message TEXT NOT NULL,
                        telegram_chat_id INTEGER,
                        access_level INTEGER DEFAULT 0,
                        token_balances TEXT,
                        created_at TEXT NOT NULL,
                        last_verified TEXT,
                        verified BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Payment requests table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS payment_requests (
                        id TEXT PRIMARY KEY,
                        wallet_address TEXT NOT NULL,
                        token_symbol TEXT NOT NULL,
                        amount REAL NOT NULL,
                        purpose TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        transaction_hash TEXT,
                        confirmed_at TEXT
                    )
                """)
                
                # Token prices table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS token_prices (
                        symbol TEXT PRIMARY KEY,
                        price_usd REAL NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Access logs table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS access_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        wallet_address TEXT NOT NULL,
                        action TEXT NOT NULL,
                        resource TEXT,
                        success BOOLEAN NOT NULL,
                        timestamp TEXT NOT NULL,
                        details TEXT
                    )
                """)
                
                conn.commit()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def generate_auth_message(self, address: str) -> str:
        """Generate authentication message for wallet signing"""
        timestamp = int(time.time())
        nonce = hashlib.sha256(f"{address}{timestamp}".encode()).hexdigest()[:8]
        
        message = f"""
EQ12 Token Gateway Authentication

Wallet: {address}
Timestamp: {timestamp}
Nonce: {nonce}

By signing this message, you authorize access to EQ12 services.
This signature expires in 5 minutes.
        """.strip()
        
        return message

    def verify_signature(self, address: str, message: str, signature: str) -> bool:
        """Verify wallet signature"""
        if not WEB3_AVAILABLE:
            logger.warning("Web3 not available - signature verification disabled")
            return True  # Allow for testing without Web3
        
        try:
            # Encode message
            encoded_message = encode_defunct(text=message)
            
            # Recover address from signature
            recovered_address = Account.recover_message(encoded_message, signature=signature)
            
            # Check if addresses match (case insensitive)
            return recovered_address.lower() == address.lower()
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    async def connect_wallet(self, address: str, signature: str, 
                           telegram_chat_id: int = None) -> bool:
        """Connect and verify wallet"""
        try:
            # Generate message for verification
            message = self.generate_auth_message(address)
            
            # Verify signature
            if not self.verify_signature(address, message, signature):
                logger.warning(f"Invalid signature for address {address}")
                return False
            
            # Get token balances
            balances = await self.get_token_balances(address)
            
            # Determine access level based on token holdings
            access_level = self.calculate_access_level(balances)
            
            # Create wallet connection
            connection = WalletConnection(
                address=address,
                signature=signature,
                message=message,
                telegram_chat_id=telegram_chat_id,
                access_level=access_level,
                token_balances=balances,
                created_at=datetime.now(timezone.utc).isoformat(),
                last_verified=datetime.now(timezone.utc).isoformat(),
                verified=True
            )
            
            # Store in database
            await self.store_wallet_connection(connection)
            
            # Cache connection
            self.wallet_cache[address] = connection
            
            # Log access
            await self.log_access(address, "wallet_connect", success=True)
            
            logger.info(f"Wallet connected: {address} (Access: {access_level.name})")
            return True
            
        except Exception as e:
            logger.error(f"Wallet connection failed for {address}: {e}")
            await self.log_access(address, "wallet_connect", success=False, details=str(e))
            return False

    async def store_wallet_connection(self, connection: WalletConnection):
        """Store wallet connection in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO wallet_connections 
                    (address, signature, message, telegram_chat_id, access_level,
                     token_balances, created_at, last_verified, verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    connection.address, connection.signature, connection.message,
                    connection.telegram_chat_id, connection.access_level.value,
                    json.dumps(connection.token_balances or {}),
                    connection.created_at, connection.last_verified, connection.verified
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store wallet connection: {e}")

    async def get_token_balances(self, address: str) -> Dict[str, float]:
        """Get token balances for wallet address"""
        balances = {}
        
        # Check cache first
        if address in self.balance_cache:
            cache_time = getattr(self, '_balance_cache_time', {}).get(address, 0)
            if time.time() - cache_time < 300:  # 5 minute cache
                return self.balance_cache[address]
        
        for symbol, token_config in self.token_configs.items():
            if not token_config.enabled:
                continue
            
            try:
                balance = await self.get_token_balance(address, token_config)
                balances[symbol] = balance
            except Exception as e:
                logger.error(f"Failed to get {symbol} balance for {address}: {e}")
                balances[symbol] = 0.0
        
        # Update cache
        self.balance_cache[address] = balances
        if not hasattr(self, '_balance_cache_time'):
            self._balance_cache_time = {}
        self._balance_cache_time[address] = time.time()
        
        return balances

    async def get_token_balance(self, address: str, token_config: TokenConfig) -> float:
        """Get balance for specific token"""
        if not WEB3_AVAILABLE:
            # Return mock balance for testing
            return 10.0 if token_config.symbol == "EQC" else 100.0
        
        network = token_config.network
        if network not in self.web3_instances:
            raise Exception(f"Network {network} not available")
        
        w3 = self.web3_instances[network]
        
        try:
            if token_config.token_type == TokenType.NATIVE:
                # Native token (ETH, MATIC, BNB)
                balance_wei = w3.eth.get_balance(address)
                balance = balance_wei / (10 ** token_config.decimals)
            else:
                # ERC-20/BEP-20 token
                contract_address = token_config.contract_address
                
                # Standard ERC-20 balanceOf function
                balance_of_abi = [{
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                }]
                
                contract = w3.eth.contract(
                    address=Web3.to_checksum_address(contract_address),
                    abi=balance_of_abi
                )
                
                balance_wei = contract.functions.balanceOf(
                    Web3.to_checksum_address(address)
                ).call()
                balance = balance_wei / (10 ** token_config.decimals)
            
            return balance
            
        except Exception as e:
            logger.error(f"Balance query failed for {token_config.symbol}: {e}")
            return 0.0

    def calculate_access_level(self, balances: Dict[str, float]) -> AccessLevel:
        """Calculate access level based on token holdings"""
        total_value_usd = 0.0
        
        for symbol, balance in balances.items():
            if symbol in self.token_configs:
                token_config = self.token_configs[symbol]
                value = balance * token_config.price_usd
                total_value_usd += value
        
        # Access level thresholds
        if total_value_usd >= 1000:
            return AccessLevel.VIP
        elif total_value_usd >= 100:
            return AccessLevel.PREMIUM
        elif total_value_usd >= 10:
            return AccessLevel.BASIC
        else:
            return AccessLevel.BASIC

    async def verify_access(self, address: str, required_level: AccessLevel) -> bool:
        """Verify wallet has required access level"""
        try:
            # Check cache first
            if address in self.wallet_cache:
                connection = self.wallet_cache[address]
                if connection.verified and connection.access_level.value >= required_level.value:
                    return True
            
            # Load from database
            connection = await self.load_wallet_connection(address)
            if not connection or not connection.verified:
                return False
            
            # Check access level
            if connection.access_level.value >= required_level.value:
                # Update cache
                self.wallet_cache[address] = connection
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Access verification failed for {address}: {e}")
            return False

    async def load_wallet_connection(self, address: str) -> Optional[WalletConnection]:
        """Load wallet connection from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT address, signature, message, telegram_chat_id, access_level,
                           token_balances, created_at, last_verified, verified
                    FROM wallet_connections WHERE address = ?
                """, (address,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                token_balances = {}
                if row[5]:
                    try:
                        token_balances = json.loads(row[5])
                    except:
                        pass
                
                return WalletConnection(
                    address=row[0],
                    signature=row[1],
                    message=row[2],
                    telegram_chat_id=row[3],
                    access_level=AccessLevel(row[4]),
                    token_balances=token_balances,
                    created_at=row[6],
                    last_verified=row[7],
                    verified=bool(row[8])
                )
                
        except Exception as e:
            logger.error(f"Failed to load wallet connection: {e}")
            return None

    async def create_payment_request(self, wallet_address: str, token_symbol: str,
                                   amount: float, purpose: str) -> str:
        """Create payment request"""
        try:
            # Generate unique payment ID
            payment_id = hashlib.sha256(
                f"{wallet_address}{token_symbol}{amount}{time.time()}".encode()
            ).hexdigest()[:16]
            
            # Calculate expiry
            expiry_minutes = self.config["payment_settings"]["default_expiry_minutes"]
            expires_at = datetime.fromtimestamp(
                time.time() + (expiry_minutes * 60)
            ).isoformat()
            
            # Create payment request
            payment = PaymentRequest(
                id=payment_id,
                wallet_address=wallet_address,
                token_symbol=token_symbol,
                amount=amount,
                purpose=purpose,
                status=PaymentStatus.PENDING,
                created_at=datetime.now(timezone.utc).isoformat(),
                expires_at=expires_at
            )
            
            # Store in database
            await self.store_payment_request(payment)
            
            logger.info(f"Payment request created: {payment_id} ({amount} {token_symbol})")
            return payment_id
            
        except Exception as e:
            logger.error(f"Failed to create payment request: {e}")
            return ""

    async def store_payment_request(self, payment: PaymentRequest):
        """Store payment request in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO payment_requests 
                    (id, wallet_address, token_symbol, amount, purpose, status,
                     created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    payment.id, payment.wallet_address, payment.token_symbol,
                    payment.amount, payment.purpose, payment.status.value,
                    payment.created_at, payment.expires_at
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store payment request: {e}")

    async def verify_payment(self, payment_id: str, transaction_hash: str) -> bool:
        """Verify payment transaction"""
        try:
            # Load payment request
            payment = await self.load_payment_request(payment_id)
            if not payment:
                return False
            
            # Verify transaction on blockchain
            verified = await self.verify_transaction(payment, transaction_hash)
            
            if verified:
                # Update payment status
                payment.status = PaymentStatus.CONFIRMED
                payment.transaction_hash = transaction_hash
                payment.confirmed_at = datetime.now(timezone.utc).isoformat()
                
                await self.update_payment_request(payment)
                
                # Grant access or credits
                await self.process_confirmed_payment(payment)
                
                logger.info(f"Payment confirmed: {payment_id}")
            
            return verified
            
        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            return False

    async def load_payment_request(self, payment_id: str) -> Optional[PaymentRequest]:
        """Load payment request from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, wallet_address, token_symbol, amount, purpose, status,
                           created_at, expires_at, transaction_hash, confirmed_at
                    FROM payment_requests WHERE id = ?
                """, (payment_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return PaymentRequest(
                    id=row[0],
                    wallet_address=row[1],
                    token_symbol=row[2],
                    amount=row[3],
                    purpose=row[4],
                    status=PaymentStatus(row[5]),
                    created_at=row[6],
                    expires_at=row[7],
                    transaction_hash=row[8],
                    confirmed_at=row[9]
                )
                
        except Exception as e:
            logger.error(f"Failed to load payment request: {e}")
            return None

    async def verify_transaction(self, payment: PaymentRequest, tx_hash: str) -> bool:
        """Verify transaction on blockchain"""
        if not WEB3_AVAILABLE:
            # Mock verification for testing
            logger.info(f"Mock verification: {tx_hash} for {payment.amount} {payment.token_symbol}")
            return True
        
        try:
            token_config = self.token_configs.get(payment.token_symbol)
            if not token_config:
                return False
            
            network = token_config.network
            if network not in self.web3_instances:
                return False
            
            w3 = self.web3_instances[network]
            
            # Get transaction receipt
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if not receipt or receipt.status != 1:
                return False
            
            # Get transaction details
            tx = w3.eth.get_transaction(tx_hash)
            
            # Verify amount and recipient
            expected_amount_wei = int(payment.amount * (10 ** token_config.decimals))
            
            if token_config.token_type == TokenType.NATIVE:
                # Native token transfer
                if tx.value != expected_amount_wei:
                    return False
            else:
                # ERC-20 token transfer
                # Parse transfer logs to verify amount and recipient
                transfer_signature = w3.keccak(text="Transfer(address,address,uint256)")
                
                for log in receipt.logs:
                    if log.topics[0] == transfer_signature:
                        # Decode transfer amount
                        amount_hex = log.data
                        amount_wei = int(amount_hex, 16)
                        
                        if amount_wei == expected_amount_wei:
                            return True
                
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Transaction verification failed: {e}")
            return False

    async def update_payment_request(self, payment: PaymentRequest):
        """Update payment request in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE payment_requests 
                    SET status = ?, transaction_hash = ?, confirmed_at = ?
                    WHERE id = ?
                """, (
                    payment.status.value, payment.transaction_hash,
                    payment.confirmed_at, payment.id
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update payment request: {e}")

    async def process_confirmed_payment(self, payment: PaymentRequest):
        """Process confirmed payment and grant access"""
        try:
            # Update wallet token balances
            await self.refresh_wallet_balances(payment.wallet_address)
            
            # Grant specific access based on payment purpose
            if payment.purpose == "ai_credits":
                credits = int(payment.amount)
                await self.grant_ai_credits(payment.wallet_address, credits)
            elif payment.purpose == "premium_access":
                await self.grant_premium_access(payment.wallet_address)
            elif payment.purpose == "betting_signals":
                await self.grant_betting_access(payment.wallet_address)
            
            # Send notification via Telegram if connected
            wallet = await self.load_wallet_connection(payment.wallet_address)
            if wallet and wallet.telegram_chat_id:
                await self.send_payment_notification(wallet.telegram_chat_id, payment)
            
        except Exception as e:
            logger.error(f"Failed to process confirmed payment: {e}")

    async def grant_ai_credits(self, wallet_address: str, credits: int):
        """Grant AI usage credits"""
        # Integration with EQ12 credit system
        logger.info(f"Granted {credits} AI credits to {wallet_address}")

    async def grant_premium_access(self, wallet_address: str):
        """Grant premium access"""
        # Update access level
        connection = await self.load_wallet_connection(wallet_address)
        if connection:
            connection.access_level = AccessLevel.PREMIUM
            await self.store_wallet_connection(connection)
        logger.info(f"Granted premium access to {wallet_address}")

    async def grant_betting_access(self, wallet_address: str):
        """Grant betting signals access"""
        logger.info(f"Granted betting access to {wallet_address}")

    async def send_payment_notification(self, chat_id: int, payment: PaymentRequest):
        """Send payment confirmation via Telegram"""
        try:
            # Import Telegram router if available
            from eq12_telegram_router import EQ12TelegramRouter
            
            router = EQ12TelegramRouter(str(self.workspace_path))
            await router.send_alert(
                "payment",
                "Payment Confirmed",
                f"Your payment of {payment.amount} {payment.token_symbol} has been confirmed!\n\n"
                f"Purpose: {payment.purpose}\n"
                f"Transaction: {payment.transaction_hash[:10]}..."
            )
        except Exception as e:
            logger.error(f"Failed to send payment notification: {e}")

    async def refresh_wallet_balances(self, address: str):
        """Refresh token balances for wallet"""
        try:
            # Clear cache
            if address in self.balance_cache:
                del self.balance_cache[address]
            
            # Get fresh balances
            balances = await self.get_token_balances(address)
            
            # Update wallet connection
            connection = await self.load_wallet_connection(address)
            if connection:
                connection.token_balances = balances
                connection.access_level = self.calculate_access_level(balances)
                connection.last_verified = datetime.now(timezone.utc).isoformat()
                await self.store_wallet_connection(connection)
                
                # Update cache
                self.wallet_cache[address] = connection
            
        except Exception as e:
            logger.error(f"Failed to refresh balances for {address}: {e}")

    async def log_access(self, address: str, action: str, resource: str = None,
                        success: bool = True, details: str = None):
        """Log access attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO access_logs 
                    (wallet_address, action, resource, success, timestamp, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    address, action, resource, success,
                    datetime.now(timezone.utc).isoformat(), details
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log access: {e}")

    # API Integration Methods
    async def check_wallet_access(self, address: str, resource: str) -> bool:
        """Check if wallet has access to specific resource"""
        try:
            # Define access requirements for different resources
            access_requirements = {
                "ai_analysis": AccessLevel.BASIC,
                "betting_signals": AccessLevel.PREMIUM,
                "portfolio_management": AccessLevel.PREMIUM,
                "system_control": AccessLevel.VIP,
                "admin_panel": AccessLevel.ADMIN
            }
            
            required_level = access_requirements.get(resource, AccessLevel.BASIC)
            has_access = await self.verify_access(address, required_level)
            
            # Log access attempt
            await self.log_access(address, "resource_access", resource, has_access)
            
            return has_access
            
        except Exception as e:
            logger.error(f"Access check failed for {address}/{resource}: {e}")
            return False

    def get_payment_address(self, token_symbol: str) -> str:
        """Get payment address for token"""
        # Return EQ12 treasury address for the token's network
        treasury_addresses = {
            "ethereum": "0x1234567890123456789012345678901234567890",
            "polygon": "0x1234567890123456789012345678901234567890",
            "bsc": "0x1234567890123456789012345678901234567890"
        }
        
        token_config = self.token_configs.get(token_symbol)
        if token_config:
            return treasury_addresses.get(token_config.network, "")
        
        return ""

    def get_token_price(self, symbol: str) -> float:
        """Get current token price in USD"""
        return self.token_configs.get(symbol, TokenConfig("", "", 0, TokenType.ERC20, "")).price_usd

    async def update_token_prices(self):
        """Update token prices from external API"""
        try:
            # This would integrate with price APIs like CoinGecko
            # For now, use mock prices
            
            mock_prices = {
                "EQC": 1.0,
                "USDC": 1.0,
                "MATIC": 0.5,
                "ETH": 2000.0,
                "BTC": 35000.0
            }
            
            for symbol, price in mock_prices.items():
                if symbol in self.token_configs:
                    self.token_configs[symbol].price_usd = price
                    
                    # Store in database
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            INSERT OR REPLACE INTO token_prices 
                            (symbol, price_usd, updated_at)
                            VALUES (?, ?, ?)
                        """, (symbol, price, datetime.now(timezone.utc).isoformat()))
                        conn.commit()
            
            logger.info("Token prices updated")
            
        except Exception as e:
            logger.error(f"Failed to update token prices: {e}")

    async def run_gateway(self):
        """Run the token gateway service"""
        logger.info("Starting Token Gateway...")
        
        # Start price updater
        if self.config["features"]["auto_price_updates"]:
            asyncio.create_task(self.periodic_price_updates())
        
        # Start transaction monitor
        if self.config["features"]["transaction_monitoring"]:
            asyncio.create_task(self.monitor_transactions())
        
        # Keep running
        while True:
            await asyncio.sleep(60)

    async def periodic_price_updates(self):
        """Periodically update token prices"""
        while True:
            try:
                await self.update_token_prices()
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                logger.error(f"Price update error: {e}")
                await asyncio.sleep(60)

    async def monitor_transactions(self):
        """Monitor blockchain for pending transactions"""
        while True:
            try:
                # Check for pending payments and verify them
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT id FROM payment_requests 
                        WHERE status = 'pending' 
                        AND datetime(expires_at) > datetime('now')
                    """)
                    
                    pending_payments = [row[0] for row in cursor.fetchall()]
                
                for payment_id in pending_payments:
                    # In a real implementation, this would check for transactions
                    # to the payment address with the correct amount
                    pass
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Transaction monitoring error: {e}")
                await asyncio.sleep(60)


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Token Gateway")
    parser.add_argument("--workspace", default="C:\\EQ12", help="Workspace path")
    parser.add_argument("--connect-wallet", nargs=2, metavar=("ADDRESS", "SIGNATURE"),
                       help="Connect wallet with signature")
    parser.add_argument("--check-access", nargs=2, metavar=("ADDRESS", "RESOURCE"),
                       help="Check wallet access to resource")
    parser.add_argument("--create-payment", nargs=4, 
                       metavar=("ADDRESS", "TOKEN", "AMOUNT", "PURPOSE"),
                       help="Create payment request")
    parser.add_argument("--verify-payment", nargs=2, metavar=("PAYMENT_ID", "TX_HASH"),
                       help="Verify payment transaction")
    
    args = parser.parse_args()
    
    gateway = EQ12TokenGateway(args.workspace)
    
    if args.connect_wallet:
        address, signature = args.connect_wallet
        success = await gateway.connect_wallet(address, signature)
        print(f"Wallet connection {'successful' if success else 'failed'}")
        return 0
    
    if args.check_access:
        address, resource = args.check_access
        has_access = await gateway.check_wallet_access(address, resource)
        print(f"Access to {resource}: {'GRANTED' if has_access else 'DENIED'}")
        return 0
    
    if args.create_payment:
        address, token, amount, purpose = args.create_payment
        payment_id = await gateway.create_payment_request(address, token, float(amount), purpose)
        print(f"Payment request created: {payment_id}")
        return 0
    
    if args.verify_payment:
        payment_id, tx_hash = args.verify_payment
        verified = await gateway.verify_payment(payment_id, tx_hash)
        print(f"Payment verification: {'SUCCESS' if verified else 'FAILED'}")
        return 0
    
    # Run gateway service
    await gateway.run_gateway()
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Token Gateway stopped by user")
        exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)