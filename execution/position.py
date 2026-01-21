"""
Position Module

This module defines the `Position` data model used by the execution/portfolio layer
to represent an open holding in a single financial instrument.

The module defines:
    - Position: A lightweight container for:
        * `instrument`: The associated `Instrument`
        * `quantity`: Current position size (units held)
        * `average_price`: Weighted-average entry price (cost basis per unit)

Behavior:
    - `update(quantity, price)`: Applies a BUY fill by increasing quantity and
      recalculating the weighted-average entry price.
    - `reduce(quantity, price)`: Applies a SELL fill by decreasing quantity and
      returning realized PnL for that sale:
        PnL = (sell_price - average_price) * quantity_sold

Notes:
    - `market_value` is currently a placeholder. In a production system, this would
      be computed using a live/mark price (or passed in) rather than returning 0.0.
    - This class intentionally focuses on per-instrument position math; higher-level
      portfolio accounting (cash, realized PnL aggregation, equity) is handled by
      `execution.portfolio.Portfolio`.
"""

# quant_engine/execution/position.py

from dataclasses import dataclass
from core.instrument import Instrument

@dataclass
class Position:
    instrument: Instrument
    quantity: float = 0.0
    average_price: float = 0.0

    @property
    def market_value(self) -> float:
        """
        Placeholder: In a real system, you'd inject the live price here.
        For now, this might represent Book Value (Cost Basis).
        """
        return 0.0
    
    @property
    def total_book_value(self) -> float:
        """
        Returns the total book value of the position.
        """
        return self.quantity * self.average_price

    def update(self, quantity: float, price: float):
        """
        Called when we BUY more shares.
        Calculates Weighted Average Price.
        """
        # 1. Calculate cost of what we ALREADY own
        previous_total_cost = self.quantity * self.average_price
        
        # 2. Calculate cost of what we represent BUYING
        new_trade_cost = quantity * price
        
        # 3. Update the total quantity
        self.quantity += quantity
        
        # 4. Calculate new weighted average (Total Cost / Total Qty)
        if self.quantity > 0:
            self.average_price = (previous_total_cost + new_trade_cost) / self.quantity

    def reduce(self, quantity: float, price: float) -> float:
        """
        Called when we SELL shares.
        Returns the Realized PnL from this specific sale.
        """
        if quantity > self.quantity:
            raise ValueError(f"Cannot sell {quantity}, only have {self.quantity}")

        # PnL = (Sell Price - Entry Price) * Quantity Sold
        pnl = (price - self.average_price) * quantity
        
        self.quantity -= quantity
        
        # Note: Selling does NOT change the Average Entry Price!
        return pnl