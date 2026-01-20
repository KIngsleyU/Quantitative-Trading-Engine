# Blueprint for trading logic

"""
Strategy Module

This module defines the strategy layer of the Quantitative Trading Engine. It provides
an abstract base class for trading strategies and a simple example implementation, so
that trading logic can be written independently of instruments, exchanges, and execution.

The module defines:
    - TradingSignal: Immutable value object representing a discrete trading decision
      (instrument, side, and optional strength)
    - Strategy: Abstract base class specifying the lifecycle of a strategy
      (`on_start`, `on_market_data`, `on_stop`) and subscription to instruments
    - BuyTheDipStrategy: Example concrete strategy that generates BUY signals when
      price falls below a configured threshold

Design goals:
    - Separation of Concerns: Strategies focus only on decision-making; they do not
      handle orders, risk, or exchange connectivity
    - Extensibility: New strategies (momentum, mean reversion, etc.) can be added by
      subclassing `Strategy` and implementing the required hooks
    - Testability: Strategies can be unit-tested by feeding synthetic market data into
      `on_market_data` and inspecting the generated `TradingSignal` objects

Example:
    >>> from core.strategy import BuyTheDipStrategy
    >>> from core.instrument import Equity
    >>> strat = BuyTheDipStrategy("Buy the Dip - AAPL")
    >>> aapl = Equity.from_api_data({...})
    >>> strat.subscribe(aapl)
    >>> strat.on_start()
    >>> signal = strat.on_market_data(aapl, price=140.0)
    >>> if signal:
    ...     print(signal.side, signal.instrument.symbol, signal.strength)
"""

# quant_engine/core/strategy.py
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional
from core.instrument import Instrument

@dataclass(frozen=True)
class TradingSignal:
    instrument: Instrument
    side: str   # "BUY" or "SELL"
    strength: float = 1.0

class Strategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.instruments: List[Instrument] = []

    def subscribe(self, instrument: Instrument):
        """Register an instrument to watch."""
        print(f"[{self.name}] Subscribing to data for {instrument.symbol}")
        self.instruments.append(instrument)

    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def on_market_data(self, instrument: Instrument, price: float) -> Optional[TradingSignal]:
        pass

    @abstractmethod
    def on_stop(self):
        pass

class BuyTheDipStrategy(Strategy):
    """
    A simple strategy: If price drops below a threshold, BUY.
    """
    def on_start(self):
        print(f"[{self.name}] Warming up indicators...")
        self.entry_threshold = 145.00 # Set specifically for our AAPL example
        
    def on_market_data(self, instrument: Instrument, price: float) -> TradingSignal | None:
        if price < self.entry_threshold:
            print(f"[{self.name}] Price {price} is below threshold {self.entry_threshold}!")
            return TradingSignal(instrument, "BUY", strength=1.0)
        return None

    def on_stop(self):
        print(f"[{self.name}] Trading session ended.")