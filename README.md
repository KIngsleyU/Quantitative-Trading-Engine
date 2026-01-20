# Quantitative Trading Engine

A production-grade, object-oriented trading engine designed for institutional quantitative trading. Built with modularity, robustness, and extensibility as core principles, this engine provides a framework for developing, backtesting, and executing algorithmic trading strategies across multiple asset classes.

## Overview

This Quantitative Trading Engine is architected to meet the reliability, speed, and data management requirements of professional trading environments. The system emphasizes clean separation of concerns, allowing traders and developers to swap strategies, exchanges, and risk management modules without affecting other components.

### Key Design Philosophy

The engine follows a **modular architecture** where:
- **Strategies** are pluggable and interchangeable
- **Exchange interfaces** abstract away market-specific implementations
- **Risk management** is centralized and enforced
- **Instruments** are type-safe and immutable

## Architecture

### Object-Oriented Design Principles

The engine is built around the "Big Four" OOP concepts:

#### 1. **Abstraction** - Exchange Interfaces
The system abstracts market connectivity through exchange interfaces, allowing seamless switching between:
- Live exchanges (Binance, Interactive Brokers, etc.)
- Paper trading environments
- Backtesting simulators

#### 2. **Polymorphism** - Strategy Engine
Multiple trading strategies can run simultaneously, all conforming to a common `TradingStrategy` interface. The engine treats each strategy uniformly, requesting signals regardless of their internal logic (moving averages, mean reversion, sentiment analysis, etc.).

#### 3. **Encapsulation** - Risk Management
Critical risk parameters are encapsulated within dedicated modules. Strategies cannot directly modify portfolio state; all trades must pass through risk management checks before execution. This prevents buggy strategies from affecting account balances or violating risk limits.

#### 4. **Inheritance** - Financial Instruments
The instrument hierarchy uses inheritance to model different asset classes while sharing common traits (symbol, price validation, tick size). Each instrument type (Equity, Future, Option, Crypto, Forex) extends the base `Instrument` class with asset-specific properties.

## Project Structure

```
Quantitative-Trading-Engine/
├── core/                    # Core domain models and interfaces
│   ├── instrument.py        # Instrument hierarchy (Equity, Future, Option, Crypto, Forex)
│   ├── strategy.py          # Base strategy interface and core strategy definitions
│   └── exchange.py          # Exchange interface abstraction
├── execution/               # Trade execution and portfolio management
│   └── portfolio.py         # Portfolio tracking and risk management
├── strategies/              # Trading strategy implementations
│   ├── buy_the_dip.py       # Example: Buy-the-dip strategy implementation
│   └── moving_average.py    # Placeholder for moving average crossover strategy
└── main.py                  # Application entry point and examples
```

## Core Components

### Instruments (`core/instrument.py`)

The instrument module provides a type-safe, immutable representation of financial instruments. All instruments are frozen dataclasses, ensuring thread-safety and preventing accidental modifications during trading operations.

#### Supported Asset Classes

- **Equity**: Stocks with dividend yield tracking
- **Future**: Futures contracts with expiration dates
- **Option**: Options with expiration dates and strike prices
- **Crypto**: Cryptocurrency pairs
- **Forex**: Foreign exchange currency pairs
- **Bond, ETF, Fund, Index, Commodity, Warrant**: Additional asset classes defined in the enum

#### Features

- **Type Safety**: Enums for `AssetClass` and `Currency` prevent invalid values
- **Compliance Fields**: ISIN and CUSIP support for regulatory requirements
- **Market Structure**: Tick size, lot size, and minimum order quantity enforcement
- **Valuation Logic**: Built-in calculation methods for notional value
- **Price Validation**: Automatic tick size validation and rounding

#### Example Usage

```python
from core.instrument import Equity, AssetClass

# Create an equity from API data
aapl = Equity.from_api_data({
    "symbol": "AAPL",
    "asset_class": "EQUITY",
    "exchange_code": "NASDAQ",
    "dividend_yield": 0.02
})

# Calculate notional value
value = aapl.calculate_value(price=150.00, quantity=10)
print(f"Notional value: ${value:,.2f}")

# Validate price against tick size
is_valid = aapl.is_price_valid(150.01)  # True if tick_size = 0.01
```

### Strategy Framework (`core/strategy.py`)

The strategy module defines the core abstraction for trading logic and provides a concrete example implementation.

#### Components

- **TradingSignal**: Immutable value object representing a trading decision (instrument, side, strength)
- **Strategy**: Abstract base class defining the lifecycle of a strategy:
  - `on_start()`: Initialization and warm-up logic
  - `on_market_data(instrument, price)`: Core decision-making hook, returns an optional `TradingSignal`
  - `on_stop()`: Cleanup and shutdown logic

This allows the engine to run multiple strategies concurrently and evaluate their signals uniformly and independently of exchanges or execution.

### Exchange Interface (`core/exchange.py`)

The exchange module provides an abstraction layer for market connectivity, implementing the abstraction pattern to decouple trading strategies from specific exchange implementations.

#### Implementations

- **PaperExchange**: Simulated exchange for testing and backtesting without real trades
- **BinanceExchange**: Implementation for Binance cryptocurrency exchange (crypto assets)
- **InteractiveBrokersExchange**: Implementation for Interactive Brokers multi-asset platform (equities, forex)
- **CMEExchange**: Implementation for Chicago Mercantile Exchange (futures contracts)

#### Features

- **Unified Interface**: All exchanges implement the same `Exchange` abstract base class
- **Vendor Independence**: Switch brokers without rewriting strategies
- **Testability**: Paper trading for safe testing without real capital
- **Polymorphism**: Strategies call the same methods regardless of exchange type
- **Connection Management**: Built-in connection state tracking

#### Example Usage

```python
from core.exchange import PaperExchange, BinanceExchange, InteractiveBrokersExchange
from core.instrument import Equity, Crypto, Future

# Initialize different exchanges
paper = PaperExchange("Test Account")
binance = BinanceExchange("Binance Real Acct")
ibkr = InteractiveBrokersExchange("IBKR Pro")

# Connect to exchanges
paper.connect()
binance.connect()
ibkr.connect()

# Get market prices (polymorphism - same interface)
equity = Equity.from_api_data({...})
price = ibkr.get_market_price(equity)

crypto = Crypto.from_api_data({...})
crypto_price = binance.get_market_price(crypto)

# Place orders (polymorphism - same interface)
order_id = paper.place_order(equity, 10.0, "BUY")
```

### Portfolio Management (`execution/portfolio.py`)

*Status: Placeholder - To be implemented*

Will provide centralized portfolio tracking, position management, and risk monitoring. Will ensure all trades comply with risk limits before execution.

### Strategy Implementations (`strategies/`)

The strategies package contains concrete implementations of the `Strategy` abstraction.

#### Implementations

- **BuyTheDipStrategy** (`strategies/buy_the_dip.py`): Buys when price falls below a configured threshold
- **moving_average.py**: Placeholder for a moving average crossover strategy

These strategies can be extended or replaced without changing the engine core, as long as they conform to the `Strategy` interface.

## Installation

### Prerequisites

- Python 3.11 or higher (required for `StrEnum` support)
- pip or your preferred package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Quantitative-Trading-Engine
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

   Note: Currently, all dependencies are from Python's standard library, so no external packages are required.

4. Run the example:
```bash
python main.py
```

## Usage Examples

### Creating Instruments

```python
from core.instrument import Equity, Future, Option, Crypto, Forex
from core.instrument import AssetClass, Currency

# Create equity
equity = Equity.from_api_data({
    "symbol": "AAPL",
    "asset_class": "EQUITY",
    "exchange_code": "NASDAQ",
    "dividend_yield": 0.025
})

# Create future contract
future = Future.from_api_data({
    "symbol": "ESZ26",
    "asset_class": "FUTURE",
    "exchange_code": "CME",
    "expiration_date": "2026-12-18",
    "multiplier": 50.0,
    "tick_size": 0.25
})

# Create option
option = Option.from_api_data({
    "symbol": "AAPL240119C00150000",
    "asset_class": "OPTION",
    "exchange_code": "CBOE",
    "expiration_date": "2024-01-19",
    "strike_price": 150.0
})
```

### Polymorphic Instrument Handling

```python
# Treat all instruments uniformly
portfolio = [equity, future, option, crypto]

for instrument in portfolio:
    value = instrument.calculate_value(price=100.0, quantity=1)
    is_valid = instrument.is_price_valid(100.05)
    print(f"{instrument.symbol}: Value=${value}, Valid={is_valid}")
```

### Exchange Abstraction and Polymorphism

```python
from core.exchange import PaperExchange, BinanceExchange, InteractiveBrokersExchange, CMEExchange
from core.instrument import Equity, Crypto, Future

# Create different exchange instances (all implement Exchange interface)
exchanges = [
    PaperExchange("Simulated Paper Account"),
    BinanceExchange("Binance Real Acct"),
    InteractiveBrokersExchange("IBKR Pro"),
    CMEExchange("CME Direct")
]

# Connect to all exchanges (same interface)
for ex in exchanges:
    ex.connect()

# Polymorphism: treat all exchanges uniformly
for ex in exchanges:
    price = ex.get_market_price(instrument)
    order_id = ex.place_order(instrument, 1.0, "BUY")
```

### Running the Example

The `main.py` file demonstrates instrument creation, exchange abstraction, strategy execution, and polymorphic usage:

```bash
python main.py
```

This will:
- Create instruments using factory methods (`from_api_data()`) and direct constructors
- Demonstrate polymorphic instrument handling (treating different types uniformly)
- Calculate notional values and validate prices for a portfolio
- Initialize multiple exchange implementations (Paper, Binance, IBKR, CME)
- Demonstrate exchange abstraction and polymorphism (same interface, different implementations)
- Simulate order routing across different exchanges based on asset type
- Initialize and run a `BuyTheDipStrategy` over a stream of simulated market data
- Demonstrate the full decision loop: market data → strategy signal → (future) risk check → execution

## Development Roadmap

### Current Status

**Fully Implemented:**
- ✅ Core instrument hierarchy with inheritance (Instrument, Equity, Future, Option, Crypto, Forex)
- ✅ Type-safe enums for asset classes (`AssetClass`) and currencies (`Currency`)
- ✅ Factory methods (`from_api_data()`) for safe API data parsing
- ✅ Price validation and tick size enforcement methods
- ✅ Notional value calculation with multiplier support
- ✅ Instrument immutability (frozen dataclasses) for thread-safety
- ✅ Validation in `__post_init__` methods for asset-specific requirements
- ✅ Exchange abstraction layer with abstract base class (`Exchange`)
- ✅ Multiple exchange implementations (PaperExchange, BinanceExchange, InteractiveBrokersExchange, CMEExchange)
- ✅ Connection management and order placement interface
- ✅ Polymorphic exchange handling (same interface, different implementations)
- ✅ Strategy framework (`core/strategy.py`) with `Strategy` base class and `TradingSignal`
- ✅ Example strategy implementation (`BuyTheDipStrategy`) in both `core.strategy` and `strategies/buy_the_dip.py`
- ✅ Example usage in `main.py` demonstrating instrument, exchange, and strategy polymorphism

**Placeholders (Not Yet Implemented):**
- ⏳ Portfolio management (`execution/portfolio.py`)
- ⏳ Additional strategy implementations (`strategies/moving_average.py`, mean reversion, etc.)
- ⏳ Backtesting engine
- ⏳ Risk management module
- ⏳ Order routing system (currently manual in examples)
- ⏳ Performance analytics

### Future Enhancements

- Real-time data feed integration
- Advanced risk metrics (VaR, Sharpe ratio, drawdown analysis)
- Multi-asset portfolio optimization
- Strategy performance attribution
- Order book depth analysis
- Machine learning strategy integration

## Design Patterns

### Factory Pattern
The `from_api_data()` class methods implement the Factory pattern, providing a consistent interface for creating instruments from raw API responses while handling type conversions and defaults.

### Abstraction Pattern
The `Exchange` abstract base class (ABC) enforces a contract that all exchange implementations must follow. This allows strategies to interact with any exchange through a uniform interface, enabling seamless switching between paper trading, backtesting, and live exchanges.

### Polymorphism
Both instruments and exchanges demonstrate polymorphism:
- **Instruments**: Different asset types (Equity, Future, Option) share the same interface, enabling uniform handling
- **Exchanges**: Different exchange implementations (Paper, Binance, IBKR, CME) share the same `Exchange` interface, allowing strategies to work with any exchange without code changes

### Strategy Pattern
The strategy framework (to be implemented) will use the Strategy pattern, allowing runtime selection and swapping of trading algorithms without modifying the engine core.

### Template Method Pattern
The instrument hierarchy uses the Template Method pattern in factory methods, where base classes define the parsing algorithm and subclasses customize specific steps.

## Thread Safety

All instrument instances are **immutable** (`frozen=True`), making them inherently thread-safe. This is critical for high-frequency trading environments where multiple threads may access the same instrument data concurrently.

Exchange implementations maintain their own connection state, and in a production environment would need additional synchronization mechanisms if accessed from multiple threads simultaneously.

## Type Safety

The engine emphasizes type safety through:
- Python type hints throughout the codebase
- Enum classes (`AssetClass`, `Currency`) preventing invalid values at compile-time
- StrEnum for currency codes, allowing direct string usage in APIs while maintaining type safety
- Dataclass field validation in `__post_init__` methods for runtime checks
- Factory methods that perform type conversion and validation from raw API data
- Immutable dataclasses (`frozen=True`) preventing accidental mutation

## Dependencies

All current dependencies are from Python's standard library:
- `dataclasses` (Python 3.7+) - For immutable instrument classes
- `enum` (standard library, `StrEnum` requires Python 3.11+) - For type-safe asset classes and currencies
- `typing` (standard library, enhanced type hints) - For type annotations
- `abc` (standard library) - For abstract base classes (Exchange interface)
- `uuid` (standard library) - Used by PaperExchange for generating order IDs

No third-party packages are required. See `requirements.txt` for details.

## Contributing

This is a production-grade system. When contributing:

1. Maintain backward compatibility
2. Add type hints to all functions
3. Include docstrings following Google/NumPy style
4. Ensure thread-safety for shared resources
5. Write tests for new features
6. Follow the existing architectural patterns

## License

[Specify your license here]

## Disclaimer

**This software is for educational and research purposes only.** Trading financial instruments carries substantial risk of loss. The authors and contributors are not responsible for any trading losses incurred from using this software. Always test strategies thoroughly in a paper trading environment before deploying with real capital.

## Contact

[Your contact information or team details]
