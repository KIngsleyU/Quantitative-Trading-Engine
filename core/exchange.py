# The Exchange Layer (Abstraction): Interface for connecting to markets
"""
Exchange Module

This module provides an abstraction layer for market connectivity in the Quantitative
Trading Engine. It implements the abstraction pattern to decouple trading strategies
from specific exchange implementations, enabling seamless switching between exchanges,
paper trading, and backtesting environments.

The module defines:
    - Exchange: Abstract base class (interface) enforcing a contract for all exchanges
    - PaperExchange: Simulated exchange for testing and backtesting without real trades
    - BinanceExchange: Implementation for Binance cryptocurrency exchange
    - InteractiveBrokersExchange: Implementation for Interactive Brokers multi-asset platform
    - CMEExchange: Implementation for Chicago Mercantile Exchange futures trading

All exchange implementations must provide:
    - connect(): Establish connection to the exchange API
    - get_market_price(instrument): Fetch current market price for an instrument
    - place_order(instrument, quantity, side): Execute buy/sell orders

This abstraction solves critical production requirements:
    - Vendor Independence: Switch brokers without rewriting strategies
    - Testability: Run unit tests without executing real trades
    - Polymorphism: Strategies call the same interface regardless of exchange type
    - Safety: Paper trading allows strategy validation before live deployment

Example:
    >>> from core.exchange import PaperExchange, BinanceExchange
    >>> from core.instrument import Equity
    >>> 
    >>> paper = PaperExchange("Test Account")
    >>> paper.connect()
    >>> equity = Equity.from_api_data({"symbol": "AAPL", "asset_class": "EQUITY", ...})
    >>> price = paper.get_market_price(equity)
    >>> order_id = paper.place_order(equity, 10.0, "BUY")

Design Principles:
    - Abstraction: Strategies interact with Exchange interface, not specific APIs
    - Polymorphism: All exchanges implement the same contract, enabling uniform handling
    - Encapsulation: Exchange-specific connection details hidden from strategy code
    - Contract Enforcement: Abstract base class ensures all implementations provide required methods
"""

from abc import ABC, abstractmethod
from core.instrument import Instrument
from typing import Protocol, Dict, Optional
from datetime import datetime

class Exchange(ABC):
    """
    Abstract Base Class (Interface) for all exchanges.
    
    This enforces a strict contract: every specific exchange (Binance, CME, PaperTrading)
    MUST implement these methods.
    """
    
    def __init__(self, name: str):
        self.name = name
        self._is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the exchange API.
        """
        pass

    @abstractmethod
    def get_market_price(self, instrument: Instrument) -> float:
        """
        Fetch the current market price for a specific instrument.
        """
        pass

    @abstractmethod
    def place_order(self, instrument: Instrument, quantity: float, side: str) -> str:
        """
        Place an order. Returns an order ID string.
        side: "BUY" or "SELL"
        """
        pass
    
# --- CONCRETE IMPLEMENTATION: PAPER TRADING ---

class PaperExchange(Exchange):
    """
    A simulated exchange for testing and backtesting.
    It does not connect to a real server; it stores orders in memory.
    """
    
    def connect(self) -> bool:
        print(f"[{self.name}] Simulating connection... Connected.")
        self._is_connected = True
        return True

    def get_market_price(self, instrument: Instrument) -> float:
        # IN PRODUCTION: This would look up real historical data or live feeds.
        # FOR NOW: We return a dummy price based on the asset class to test logic.
        if "USD" in instrument.symbol: 
            return 1.0
        return 100.00 + (instrument.lot_size * 0.1) 

    def place_order(self, instrument: Instrument, quantity: float, side: str) -> str:
        if not self._is_connected:
            raise ConnectionError("Exchange not connected.")
            
        # Simulate an Order ID
        import uuid
        order_id = str(uuid.uuid4())[:8]
        
        # Calculate approximate cost
        price = self.get_market_price(instrument)
        cost = instrument.calculate_value(price, quantity)
        
        print(f"[{self.name}] {side} ORDER FILLED: {quantity}x {instrument.symbol} @ ${price:.2f}")
        print(f"   Total Notional: ${cost:,.2f}")
        
        return order_id
    
# quant_engine/core/exchange.py
# ... (Keep Imports, Exchange class, and PaperExchange class as they were) ...

# --- CONCRETE IMPLEMENTATION: CRYPTO ---
class BinanceExchange(Exchange):
    """
    Connects to Binance for Crypto trading.
    """
    def connect(self) -> bool:
        # In a real app, this would use the 'ccxt' library or binance-python sdk
        print(f"[{self.name}] Connecting to Binance API (HMAC SHA256)... Connected.")
        self._is_connected = True
        return True

    def get_market_price(self, instrument: Instrument) -> float:
        if instrument.asset_class.name != "CRYPTO":
            # In production, we might just return 0.0 or raise a warning
            print(f"[{self.name}] WARNING: Binance only supports Crypto.")
            return 0.0
        
        # Simulate live crypto pricing
        return 45000.00 if instrument.symbol == "BTC" else 3000.00

    def place_order(self, instrument: Instrument, quantity: float, side: str) -> str:
        if not self._is_connected: raise ConnectionError("Not connected.")
        
        print(f"[{self.name}] Sending REST API POST request to /api/v3/order...")
        print(f"   > {side} {quantity} {instrument.symbol}")
        
        # Simulate Binance returning an Order ID
        return "BINANCE-882910"


# --- CONCRETE IMPLEMENTATION: MULTI-ASSET BROKER ---
class InteractiveBrokersExchange(Exchange):
    """
    Connects to Interactive Brokers (IBKR) Gateway.
    IBKR supports almost all asset classes.
    """
    def connect(self) -> bool:
        # IB uses a specific socket connection (TWS API)
        print(f"[{self.name}] Connecting to TWS/IB Gateway (Port 7497)... Connected.")
        self._is_connected = True
        return True

    def get_market_price(self, instrument: Instrument) -> float:
        # IB quotes differ by asset class
        if instrument.asset_class.name == "EQUITY":
            return 155.00 # Mock AAPL price
        elif instrument.asset_class.name == "FOREX":
            return 1.10 # Mock EUR/USD
        return 0.0

    def place_order(self, instrument: Instrument, quantity: float, side: str) -> str:
        if not self._is_connected: raise ConnectionError("Not connected.")
        
        # IB orders are complex objects sent over a socket
        print(f"[{self.name}] Transmitting 'reqIds' and 'placeOrder' opcode to IB Gateway...")
        print(f"   > {side} {quantity} {instrument.symbol} on {instrument.exchange_code}")
        
        return "IB-9912"


# --- CONCRETE IMPLEMENTATION: FUTURES ---
class CMEExchange(Exchange):
    """
    Connects to the Chicago Mercantile Exchange for Futures.
    """
    def connect(self) -> bool:
        # Direct Market Access (DMA) often uses the FIX Protocol
        print(f"[{self.name}] Initializing FIX Protocol Session (QuickFIX)... Connected.")
        self._is_connected = True
        return True

    def get_market_price(self, instrument: Instrument) -> float:
        if instrument.asset_class.name != "FUTURE":
            return 0.0
        return 4550.25 # Mock ES Future price

    def place_order(self, instrument: Instrument, quantity: float, side: str) -> str:
        if not self._is_connected: raise ConnectionError("Not connected.")
        
        print(f"[{self.name}] Sending FIX message 'NewOrderSingle' (35=D)...")
        print(f"   > {side} {quantity} {instrument.symbol} (Future)")
        
        return "CME-7712"