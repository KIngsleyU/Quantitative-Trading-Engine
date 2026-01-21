"""
Portfolio Module

This module implements the portfolio layer of the Quantitative Trading Engine. It
tracks cash, open positions, and realized PnL, and updates portfolio state in response
to filled orders coming from the execution layer.

The module defines:
    - Portfolio: A class responsible for:
        * Maintaining available cash (liquidity)
        * Managing open positions per instrument
        * Accumulating realized PnL from closed trades
        * Providing utility methods for equity calculations and simple risk checks

Behavior:
    - `on_fill(...)`: Applies the effect of a filled BUY or SELL order to cash,
      positions, and realized PnL (delegating position math to `Position`).
    - `get_total_equity(...)`: Computes net worth as cash plus the mark-to-market
      value of all open positions.
    - `is_cash_enough(...)`: Performs a basic pre-trade cash check for BUY orders.
    - `get_positions()`: Prints a human-readable summary of all positions.

This module encapsulates portfolio state and separates it from strategy and exchange
logic, enabling clearer risk management and easier extension to more advanced
features (margin, leverage, multi-currency accounting, etc.).
"""

from typing import Dict, List
from core.instrument import Instrument
from execution.position import Position
class Portfolio:
    def __init__(self, initial_cash: float = 100_000.0):
        # 1. LIQUIDITY: Available money
        self.cash = initial_cash
        
        # 2. INVENTORY: Mapping Instrument -> Quantity
        # e.g., {aapl_obj: Position(quantity=10.0, average_price=150.0), btc_obj: Position(quantity=0.5, average_price=10000.0)}
        self.positions: Dict[Instrument, Position] = {}
        
        # 3. HISTORY: Total Realized PnL (Profit from closed trades)
        self.realized_pnl = 0.0

    def on_fill(self, instrument: Instrument, side: str, quantity: float, price: float):
        """
        Updates the portfolio state based on a filled order.
        """
        cost = quantity * price
        
        if side == "BUY":
            # Cash goes DOWN, Inventory goes UP
            self.cash -= cost
            
            if instrument not in self.positions:
                self.positions[instrument] = Position(instrument, quantity, price)
            else:
                self.positions[instrument].update(quantity, price)
            
            print(f"[Portfolio] BOUGHT {quantity} {instrument.symbol}. Cash Left: ${self.cash:,.2f}")       # TODO: Add the position to the portfolio

        elif side == "SELL":
            # Cash goes UP, Inventory goes DOWN
            self.cash += cost
            if instrument in self.positions:
                trade_pnl = self.positions[instrument].reduce(quantity, price)
            else:
                print(f"[Portfolio] ERROR: Tried to sell {quantity} {instrument.symbol} but it is not in the portfolio")
                return
            print(f"[Portfolio] SOLD {quantity} {instrument.symbol}. Cash: ${self.cash:,.2f}")
            
            try:
                # 3. DELEGATE: Tell Position to reduce and calculate PnL
                self.realized_pnl += trade_pnl
                print(f"[Portfolio] SOLD {quantity} {instrument.symbol}. "
                      f"Realized PnL: ${trade_pnl:.2f}. Cash: ${self.cash:,.2f}")
                if self.positions[instrument].quantity == 0:
                    del self.positions[instrument]
            except ValueError as e:
                print(f"[Portfolio] ERROR: {e}")

    def get_total_equity(self, current_prices: Dict[Instrument, float]) -> float:
        """
        Calculates Net Worth: Cash + Market Value of Holdings
        """
        market_value = 0.0
        for instrument, position in self.positions.items():
            market_value += position.quantity * current_prices.get(instrument, 0.0)
            
        return self.cash + market_value
    
    def is_cash_enough(self, instrument: Instrument, quantity: float, price: float, side: str) -> bool:
        """
        Checks if the portfolio has enough cash to buy the given quantity of the instrument.
        """
        if side == "BUY":
            print(f"[Portfolio] Checking if cash is enough to buy {quantity} {instrument.symbol} at {price:.2f}")
            print(f"[Portfolio] Cash: ${self.cash} USD")
            print(f"[Portfolio] Instrument value: {instrument.calculate_value(price, quantity):.2f} USD")
            if self.cash >= instrument.calculate_value(price, quantity):
                print(f"[Portfolio] Has enough cash to buy {quantity} {instrument.symbol}. Cash Left: ${self.cash:.2f}")
                return True
            else:
                print(f"[Portfolio] Does not have enough cash to buy {quantity} {instrument.symbol}. Cash Left: ${self.cash:,.2f}")
                return False
        print(f"[Portfolio] we are selling {quantity} {instrument.symbol} at {price:.2f}")
        return True
    def get_positions(self):
        """
        Returns the positions in the portfolio in a pretty string format
        """
        print("Portfolio Positions:")
        for instrument, position in self.positions.items():
            print(f"  {instrument.symbol}: {position.quantity} at {position.average_price:.2f} USD")
        