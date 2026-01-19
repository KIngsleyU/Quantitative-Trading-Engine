# Entry point to run the bot
from core.instrument import AssetClass, Currency, Instrument, Equity, Future, Option, Crypto, Forex
from core.exchange import Exchange, PaperExchange, BinanceExchange, InteractiveBrokersExchange, CMEExchange

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

if __name__ == "__main__":
    main()
