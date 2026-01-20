"""
Buy the Dip Strategy

This module implements a simple example trading strategy for the Quantitative Trading
Engine. The strategy monitors market prices for subscribed instruments and generates
BUY signals when the price falls below a predefined threshold.

The module defines:
    - BuyTheDipStrategy: A concrete implementation of the abstract `Strategy` base class
      that encapsulates a classic "buy the dip" behavior.

Behavior:
    - On start (`on_start`), the strategy initializes its configuration (e.g., entry
      threshold for a specific instrument like AAPL).
    - On each market data update (`on_market_data`), it compares the current price
      against the entry threshold.
    - If the price is below the threshold, it emits a `TradingSignal` with side="BUY".
    - On stop (`on_stop`), it performs any necessary cleanup or logging.

This module is intended as a reference implementation for how to build concrete
strategies on top of the core `Strategy` abstraction. More advanced strategies
can follow the same pattern while implementing their own signal logic.
"""

from core.strategy import Strategy, TradingSignal
from core.instrument import Instrument

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