"""
Financial Instrument Module

This module provides a type-safe, immutable hierarchy of financial instruments for the
Quantitative Trading Engine. It implements the inheritance pattern to model different
asset classes while maintaining shared functionality and contract enforcement.

The module defines:
    - AssetClass: Enumeration of supported asset classes (Equity, Future, Option, etc.)
    - Currency: ISO 4217 currency codes using StrEnum for type safety
    - Instrument: Base class for all financial instruments with market structure rules
    - Equity: Stock/equity instrument with dividend yield tracking
    - Future: Futures contract with expiration date
    - Option: Options contract with expiration date and strike price
    - Crypto: Cryptocurrency pair instrument
    - Forex: Foreign exchange currency pair instrument

All instruments are immutable (frozen dataclasses) for thread-safety and enforce
market rules such as tick size, lot size, and minimum order quantities. Each instrument
includes factory methods for safe creation from API data with automatic type conversion
and validation.

Example:
    >>> from core.instrument import Equity, AssetClass
    >>> equity = Equity.from_api_data({
    ...     "symbol": "AAPL",
    ...     "asset_class": "EQUITY",
    ...     "exchange_code": "NASDAQ",
    ...     "dividend_yield": 0.025
    ... })
    >>> value = equity.calculate_value(price=150.0, quantity=10)
    >>> print(f"Notional value: ${value:,.2f}")

Design Principles:
    - Immutability: All instruments are frozen to prevent accidental modification
    - Type Safety: Enums prevent invalid asset class or currency values
    - Encapsulation: Market structure logic (tick size, multipliers) built into classes
    - Inheritance: Shared functionality in base class, asset-specific traits in subclasses
"""
from dataclasses import dataclass
from enum import Enum, auto, StrEnum
from typing import Optional


class AssetClass(Enum):
    """
    Enumeration for supported asset classes.
    
    Example:
        x = AssetClass.api_string  <-- ERROR
        x = AssetClass.EQUITY  <-- Output: AssetClass.EQUITY (Enum member)
        x = AssetClass["EQUITY"]  <-- Output: AssetClass.EQUITY
    """
    EQUITY = auto()
    FUTURE = auto()
    CRYPTO = auto()
    FOREX = auto()
    OPTION = auto()
    
    BOND = auto()
    ETF = auto()
    FUND = auto()
    INDEX = auto()
    COMMODITY = auto()
    WARRANT = auto()
    
class Currency(StrEnum):
    """
    Standardized ISO 4217 currency codes.
    Using StrEnum allows these to be used directly in API strings.
    
    Example:
        x = Currency.api_string  <-- ERROR
        x = Currency.USD  <-- Output: Currency.USD
        x = Currency["USD"]  <-- Output: Currency.USD
    """
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    AUD = "AUD"
    CAD = "CAD"
    
@dataclass(frozen=True)
class Instrument:
    """
    Base class representing a financial instrument.
    
    frozen=True makes instances immutable (read-only) after creation,
    which is critical for thread-safety in high-frequency environments.
    """
    
    # 1. Identification & Classification
    symbol: str
    asset_class: AssetClass
    exchange_code: str
    
    # Optional fields for compliance (not every asset has an ISIN immediately)
    isin: Optional[str] = None
    cusip: Optional[str] = None
    
    # 2. Market Structure & Precision
    tick_size: float = 0.01
    min_order_qty: float = 1.0
    lot_size: float = 1.0
    
    # 3. Valuation & Risk Management
    quote_currency: Currency = Currency.USD
    multiplier: float = 1.0  # Standard multiplier
    
    def calculate_value(self, price: float, quantity: float) -> float:
        """
        Calculates the notional value of a position.
        Formula: Price * Quantity * Multiplier
        """
        return price * quantity * self.multiplier

    def is_price_valid(self, price: float) -> bool:
        """
        Checks if a price aligns with the instrument's tick size.
        (e.g., a price of 100.015 is invalid if tick_size is 0.01).
        """
        # Using a small epsilon for floating point comparison safety
        remainder = price % self.tick_size
        return remainder < 1e-9 or abs(remainder - self.tick_size) < 1e-9
    
    def round_to_tick(self, price: float) -> float:
        """
        Rounds a price to the nearest tick size.
        """
        return round(price / self.tick_size) * self.tick_size
    
    @staticmethod
    def parse_common_data(data: dict) -> dict:
        """
        Parses common data from a raw dictionary.
        """
        return {
            # 1. Convert Strings to Enums safely
            "symbol": data["symbol"],
            # We use .upper() to handle cases where API returns "usd" instead of "USD"
            "asset_class": AssetClass[data["asset_class"].upper()],
            "exchange_code": data["exchange_code"],
            
            # Optional fields use .get() returns None if missing
            "isin": data.get("isin"),
            "cusip": data.get("cusip"),
            
            # Parse floats safely, defaulting to class defaults if missing
            "tick_size": float(data.get("tick_size", 0.01)),
            "min_order_qty": float(data.get("min_order_qty", 1.0)),
            "lot_size": float(data.get("lot_size", 1.0)),
            
            # Valuation & Risk Management
            "quote_currency": Currency[data.get("quote_currency", "USD").upper()],
            "multiplier": float(data.get("multiplier", 1.0))
        }
    
    # --- FACTORY METHOD START ---
    @classmethod
    def from_api_data(cls, data: dict, **extra_fields) -> "Instrument":
        """
        Factory method to create an Instrument from a raw dictionary.
        Handles safe Enum conversion and defaults.
        """
        try:
            
            parsed_data = cls.parse_common_data(data)
            
            # Merge the child-specific fields (like dividend_yield) into the main data dictionary
            parsed_data.update(extra_fields)
            # 2. Extract and cast numeric types (handling potential string inputs like "100.0")
            """
            Why we use cls(...) instead of Instrument(...):
                If we used 'Instrument(...)' in the parent factory:
                FutureInstrument.from_api_data(...) would return a plain Instrument. :(

                Because we used 'cls(...)':
                FutureInstrument.from_api_data(...) returns a FutureInstrument! :)
            """
            return cls(**parsed_data)
        except KeyError as e:
            raise ValueError(f"Missing required field for Instrument: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid data format: {e}")
    # --- FACTORY METHOD END ---

@dataclass(frozen=True)
class Equity(Instrument):
    """
    Specific implementation for Stocks/Equities.
    Inherits all fields from Instrument.
    """
    dividend_yield: float = 0.0
    
    def __post_init__(self):
        """
        Post-initialization checks for equity-specific requirements.
        """
        if self.asset_class != AssetClass.EQUITY:
            raise ValueError("Equity must be an equity asset class.")
    
    @classmethod
    def from_api_data(cls, data: dict) -> "Equity":
        """
        Factory method to create an Equity from a raw dictionary.
        Handles safe Enum conversion and defaults.
        """
        # We use super() to call the parent class's from_api_data method
        # This ensures that the common data is parsed correctly
        parsed_data = super().from_api_data(
            data,
            asset_class=AssetClass.EQUITY,
            dividend_yield=float(data.get("dividend_yield", 0.0)))
        
        return parsed_data
    
@dataclass(frozen=True)
class Future(Instrument):
    """
    Specific implementation for Futures contracts.
    Requires an expiration date.
    """
    expiration_date: str = "2099-12-31" # Simple string for now, datetime later
    
    def __post_init__(self):
        if self.asset_class != AssetClass.FUTURE:
            raise ValueError("Future must have AssetClass.FUTURE")
        if not self.expiration_date:
            raise ValueError("Future must have an expiration date")
    
    @classmethod
    def from_api_data(cls, data: dict) -> "Future":
        """
        Factory method to create a Future from a raw dictionary.
        Handles safe Enum conversion and defaults.
        """
        
        
        # We use super() to call the parent class's parse_common_data method
        # This ensures that the common data is parsed correctly
        return super().from_api_data(
            data, 
            expiration_date=data.get("expiration_date", "2099-12-31"))
    
@dataclass(frozen=True)
class Option(Instrument):
    """
    Specific implementation for Options contracts.
    Requires an expiration date and strike price.
    """
    expiration_date: str = "2099-12-31" # Simple string for now, datetime later
    strike_price: float = 0.0
    
    def __post_init__(self):
        if self.asset_class != AssetClass.OPTION:
            raise ValueError("Option must have AssetClass.OPTION")
        if not self.expiration_date:
            raise ValueError("Option must have an expiration date")
        if self.strike_price <= 0:
            raise ValueError("Option must have a positive strike price")
    
    @classmethod
    def from_api_data(cls, data: dict) -> "Option":
        """
        Factory method to create an Option from a raw dictionary.
        Handles safe Enum conversion and defaults.
        """
        parsed_data = super().parse_common_data(data)
        parsed_data["expiration_date"] = data.get("expiration_date", "2099-12-31")
        parsed_data["strike_price"] = float(data.get("strike_price", 0.0))
        return cls(**parsed_data)
    
@dataclass(frozen=True)
class Crypto(Instrument):
    """
    Specific implementation for Crypto currencies.
    Requires a cryptocurrency code.
    """
    cryptocurrency_code: str = "BTC"
    
    def __post_init__(self):
        if self.asset_class != AssetClass.CRYPTO:
            raise ValueError("Crypto must have AssetClass.CRYPTO")
        if not self.cryptocurrency_code:
            raise ValueError("Crypto must have a cryptocurrency code")
    
    @classmethod
    def from_api_data(cls, data: dict) -> "Crypto":
        """
        Factory method to create a Crypto from a raw dictionary.
        Handles safe Enum conversion and defaults.
        """ 
        return cls(
            **super().parse_common_data(data),
            cryptocurrency_code=data.get("cryptocurrency_code", "BTC")
        )
    
@dataclass(frozen=True)
class Forex(Instrument):
    """
    Specific implementation for Forex currencies.
    Requires a forex code.
    """
    forex_code: str = "USD/JPY"
    
    def __post_init__(self):
        if self.asset_class != AssetClass.FOREX:
            raise ValueError("Forex must have AssetClass.FOREX")
        if not self.forex_code:
            raise ValueError("Forex must have a forex code")
    
    @classmethod
    def from_api_data(cls, data: dict) -> "Forex":
        """
        Factory method to create a Forex from a raw dictionary.
        Handles safe Enum conversion and defaults.
        """
        return cls(
            **super().parse_common_data(data),
            forex_code=data.get("forex_code", "USD/JPY")
        )

