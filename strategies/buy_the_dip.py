# quant_engine/strategies/basic_strategies.py
"""
Buy the Dip Strategy

This module implements a stateful "buy the dip" trading strategy for the
Quantitative Trading Engine. The strategy monitors subscribed instruments,
enters on price dips, and exits using take-profit and stop-loss rules.

The module defines:
    - BuyTheDipStrategy: A concrete implementation of the core `Strategy` base class
      that:
        * Buys when price falls below a configured entry threshold
        * Tracks entry prices per instrument in `active_positions`
        * Exits positions when either:
            - Take-profit is reached (price up by `take_profit_percentage`)
            - Stop-loss is hit (price down by `stop_loss_percentage`)

Behavior:
    - `on_start()`: Logs configuration (entry threshold) and prepares internal state.
    - `on_market_data(instrument, price)`: 
        * If the instrument is already in `active_positions`, evaluates PnL and
          emits a SELL `TradingSignal` on take-profit or stop-loss.
        * If the instrument is not in `active_positions` and price is below
          `entry_threshold`, emits a BUY `TradingSignal` and records the entry price.
    - `on_stop()`: Logs the end of the trading session.

This strategy serves as a reference for building more advanced, position-aware
strategies on top of the shared `Strategy` and `TradingSignal` abstractions.
"""
from core.strategy import Strategy, TradingSignal
from core.instrument import Instrument
from typing import Dict, Optional

class BuyTheDipStrategy(Strategy):
    """
    A simple strategy: 
    - BUY if price drops below entry_threshold.
    - SELL if price hits profit target OR stop loss.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.entry_threshold = 145.00
        self.take_profit_percentage = 0.02  # Sell if up 2%
        self.stop_loss_percentage = 0.01    # Sell if down 1%
        
        # We need to remember our entry price to know if we are winning or losing!
        # Mapping: Instrument -> Entry Price
        self.active_positions: Dict[Instrument, float] = {}

    def on_start(self):
        print(f"[{self.name}] Warming up... Threshold: {self.entry_threshold}")
        
    def on_market_data(self, instrument: Instrument, price: float) -> Optional[TradingSignal]:
        
        # 1. CHECK EXIT CONDITIONS (Do we own it?)
        if instrument in self.active_positions:
            entry_price = self.active_positions[instrument]
            pnl_pct = (price - entry_price) / entry_price
            
            # Take Profit (Winning)
            if pnl_pct >= self.take_profit_percentage:
                print(f"[{self.name}] TAKING PROFIT! Up {pnl_pct:.2%}")
                del self.active_positions[instrument] # We are exiting
                return TradingSignal(instrument, "SELL", strength=1.0)
            
            # Stop Loss (Losing)
            if pnl_pct <= -self.stop_loss_percentage:
                print(f"[{self.name}] STOP LOSS TRIGGERED! Down {pnl_pct:.2%}")
                del self.active_positions[instrument] # We are exiting
                return TradingSignal(instrument, "SELL", strength=1.0)

        # 2. CHECK ENTRY CONDITIONS (Do we want to buy it?)
        else:
            if price < self.entry_threshold:
                print(f"[{self.name}] Buying the dip at {price}")
                self.active_positions[instrument] = price # Record entry
                return TradingSignal(instrument, "BUY", strength=1.0)
        
        return None

    def on_stop(self):
        print(f"[{self.name}] Trading session ended.")