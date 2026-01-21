# Entry point to run the bot
from core.instrument import AssetClass, Currency, Instrument, Equity, Future, Option, Crypto, Forex
from core.exchange import Exchange, PaperExchange, BinanceExchange, InteractiveBrokersExchange, CMEExchange
from core.strategy import Strategy
from strategies.buy_the_dip import BuyTheDipStrategy
from execution.portfolio import Portfolio
def main():
    instrument1 = Instrument.from_api_data({
        "symbol": "AAPL",
        "asset_class": "EQUITY",
        "exchange_code": "NASDAQ"
    })
    print("--------------------------------")
    print("Instrument 1:")
    print(type(instrument1))
    print(instrument1)
    
    instrument2 = Instrument(
        symbol="AAPL",
        asset_class="EQUITY",
        exchange_code="NASDAQ"
    )
    print("--------------------------------")
    print("Instrument 2:")
    print(type(instrument2))
    print(instrument2)
    
    instrument3 = Equity(
        symbol="AAPL",
        asset_class=AssetClass.EQUITY,
        exchange_code="NASDAQ"
    )
    print("--------------------------------")
    print("Instrument 3:")
    print(type(instrument3))
    print(instrument3)
    
    aapl = Equity.from_api_data({
        "symbol": "AAPL",
        "asset_class": "EQUITY",
        "exchange_code": "NASDAQ",
        "dividend_yield": 0.02,
        "expiration_date": "2026-01-01",
        "strike_price": 100.0
    })
    
    print("--------------------------------")
    print("AAPL:")
    print(type(aapl))
    print(aapl)
    spy = Future.from_api_data({
        "symbol": "SPY",
        "asset_class": "FUTURE",
        "exchange_code": "CME",
        "expiration_date": "2026-01-01",
        "strike_price": 100.0
    })
    
    instrument4 = Future(
        symbol="SPY",
        asset_class=AssetClass.FUTURE,
        exchange_code="CME",
        expiration_date="2026-01-01"
    )
    print("--------------------------------")
    print("Instrument 4:")
    print(type(instrument4))
    print(instrument4)
    
    print("--------------------------------")
    print("SPY:")
    print(type(spy))
    print(spy)
    
    spy_option = Option.from_api_data({
        "symbol": "SPY",
        "asset_class": "OPTION",
        "exchange_code": "CME",
        "expiration_date": "2026-01-01",
        "strike_price": 100.0
    })
    print("SPY Option:")
    print(type(spy_option))
    print(spy_option)
    
    btc = Crypto.from_api_data({
        "symbol": "BTC",
        "asset_class": "CRYPTO",
        "exchange_code": "BITMEX",
        "cryptocurrency_code": "BTC"
    })
    print("--------------------------------")
    print("BTC:")
    print(type(btc))
    print(btc)
    
    es_future = Future.from_api_data({
        "symbol": "ESZ26",
        "asset_class": "FUTURE",
        "exchange_code": "CME",
        "expiration_date": "2026-01-01"
    })
    print("--------------------------------")
    print("ES Future:")
    print(type(es_future))
    print(es_future)
    
    portfolio = [aapl, spy, spy_option, btc]
    print()
    print("--------------------------------")
    print("Portfolio of instruments:")
    print(portfolio)
    
    # 3. Test Polymorphism (Treating different objects the same way)
    for instrument in portfolio:
        print(f"\nInstrument: {instrument.symbol} ({instrument.asset_class.name})")
        
        # Test Valuation Logic
        simulated_price = 4500.50 if instrument.symbol == "ESZ26" else 150.00
        qty = 1
        
        val = instrument.calculate_value(simulated_price, qty)
        print(f"  Notional Value of 1 unit @ {simulated_price}: ${val:,.2f}")
        
        # Test Tick Size Validation
        bad_price = 4500.12  # Invalid for ES (tick is 0.25)
        is_valid = instrument.is_price_valid(bad_price)
        print(f"  Is {bad_price} a valid price? {is_valid}")
    
    print(f"Loaded: {aapl.symbol}, {btc.symbol}, {es_future.symbol}\n")
    print()
    print("--------------------------------")
    print("Testing the Exchange Interface (Abstraction, Polymorphism)")
    print("--------------------------------")
    print("--- 2. Initializing Exchanges ---")
    
    # Notice they are all type 'Exchange', but different implementations
    exchanges = [
        PaperExchange("Simulated Paper Account"),
        BinanceExchange("Binance Real Acct"),
        InteractiveBrokersExchange("IBKR Pro"),
        CMEExchange("CME Direct")
    ]

    for ex in exchanges:
        ex.connect()
    
    print("\n--- 3. Simulating Order Routing ---")
    
    # We want to buy 1 unit of each asset.
    # We need to decide WHICH exchange to send the order to.
    
    orders_to_place = [
        (aapl, "IBKR Pro"),       # Send Stock to IB
        (btc, "Binance Real Acct"), # Send Crypto to Binance
        (es_future, "CME Direct")   # Send Future to CME
    ]

    for instrument, target_exchange_name in orders_to_place:
        print(f"\nProcessing Order for {instrument.symbol}...")
        
        # Find the correct exchange object in our list
        # (In a real bot, an 'OrderRouter' class would do this automatically)
        target_exchange = next(ex for ex in exchanges if ex.name == target_exchange_name)
        
        # Polymorphism! We call the same methods regardless of the exchange type.
        current_price = target_exchange.get_market_price(instrument)
        print(f"  Price on {target_exchange.name}: ${current_price:,.2f}")
        
        if current_price > 0:
            order_id = target_exchange.place_order(instrument, 1.0, "BUY")
            print(f"  Order Success! ID: {order_id}")
        else:
            print(f"  Order Failed: Invalid price from exchange.")# 4. Test the Exchange Interface

    print()
    print("--------------------------------")
    print("Testing the Strategy Interface (Abstraction, Polymorphism)")
    print("--------------------------------")
    print("--- 4. Initializing Strategies ---")
    
    # 1. Setup Environment
    # We use a paper exchange so we don't lose real money!
    exchange = PaperExchange("Backtest Exchange")
    exchange.connect()

    # 2. Setup Instrument
    aapl = Equity.from_api_data({
        "symbol": "AAPL", "asset_class": "EQUITY", "exchange_code": "NASDAQ",
        "dividend_yield": 0.005
    })

    portfolio = Portfolio()

    # 3. Setup Strategy
    strategy = BuyTheDipStrategy("DipBuyer_v1")
    strategy.subscribe(aapl)
    strategy.on_start()

    # 4. The Simulation Data (The "Time Machine")
    # We simulate the price dropping, then recovering
    market_data = [
        150.00, 
        148.00, 
        144.00, # <--- This should trigger our BuyTheDip (threshold is 145.00)
        146.88, 
        146.00,
        150.00
    ]

    print("\n--- BEGINNING MARKET DATA LOOP ---")
    
    # 5. The Engine Loop (Heartbeat)
    for price in market_data:
        print(f"\n[TICK] New Market Price: ${price:.2f}")
        
        # A. Feed the Brain (Inject Data)
        # We ask the strategy: "Here is the price, what do you want to do?"
        signal = strategy.on_market_data(aapl, price)
        
        # B. Check for a Signal (The Decision)
        if signal:
            print(f"  >>> SIGNAL RECEIVED: {signal.side} {signal.instrument.symbol} (Strength: {signal.strength})")
            
            # C. Risk Check Layer (The Guardrail)
            # (In the future, a RiskManager class would go here to say YES/NO)
            # For now, we assume all signals are valid.
            
            # D. Execution (The Action)
            try:
                # We place the order on the exchange
                if portfolio.is_cash_enough(signal.instrument, 10, price, signal.side):
                    order_id = exchange.place_order(
                        signal.instrument, 
                        quantity=10, 
                        side=signal.side,
                        price=price)
                    print(f"  >>> EXECUTION CONFIRMED: Order ID {order_id}")
                    portfolio.on_fill(signal.instrument, signal.side, 10, price)
            except Exception as e:
                print(f"  >>> EXECUTION FAILED: {e}")
                
        else:
            print("  ... Strategy is holding (No Signal).")

    # 4. CLEANUP: Shut down gracefully
    print("\n--- 4. Session Ended ---")
    strategy.on_stop()
    print(f"Portfolio Cash: ${portfolio.cash:.2f} USD")
    portfolio.get_positions()
    print(f"Portfolio Realized PnL: ${portfolio.realized_pnl:.2f} USD")
    print(f"Portfolio Total Equity: ${portfolio.get_total_equity({aapl: 150.00}):.2f} USD")
if __name__ == "__main__":
    main()
