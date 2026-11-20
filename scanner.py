
from datetime import datetime, timezone
import yfinance as yf
import pandas as pd

# AI Trading Scanner - Phase 2
# Real historical prices, paper trading only

CAPITAL_RM = 250.00
RISK_PERCENT = 0.02
MIN_RR = 2.0

# Example stocks from US and Bursa Malaysia
WATCHLIST = {
    "US": ["AAPL", "MSFT", "NVDA"],
    "MY": ["1155.KL", "1023.KL", "5347.KL"]
}

def analyze_stock(symbol, market):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="6mo", interval="1d")

        if df.empty or len(df) < 55:
            print(f"{symbol}: Insufficient data")
            return

        

        close = pd.to_numeric(df["Close"], errors="coerce").dropna()

        if len(close) < 55:
            print(f"{symbol}: Insufficient valid closing prices")
            return


        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()

        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(
            alpha=1/14, adjust=False,
            min_periods=14
        ).mean()
        avg_loss = loss.ewm(
            alpha=1/14, adjust=False,
            min_periods=14
        ).mean()

        if avg_loss.iloc[-1] == 0:
            rsi = 100.0 if avg_gain.iloc[-1] > 0 else 50.0
        else:
            rs = avg_gain.iloc[-1] / avg_loss.iloc[-1]
            rsi = 100 - (100 / (1 + rs))

        price = float(close.iloc[-1])
        ma20 = float(sma20.iloc[-1])
        ma50 = float(sma50.iloc[-1])

        signal = "NO TRADE"

        if price > ma20 > ma50 and 50 <= rsi <= 70:
            signal = "PAPER WATCHLIST"

        stop_loss = price * 0.95
        take_profit = price * 1.10

        # US stock prices are in USD; MY prices in MYR.
        # Do not calculate cross-currency position sizes
        # without a verified exchange rate.

        print("---------------------------")
        print("Symbol:", symbol)
        print("Market:", market)
        print("Price:", round(price, 2))
        print("SMA20:", round(ma20, 2))
        print("SMA50:", round(ma50, 2))
        print("RSI14:", round(rsi, 2))
        print("Signal:", signal)
        print("Illustrative stop:", round(stop_loss, 2))
        print("Illustrative target:", round(take_profit, 2))
        print("Risk/Reward:", "1:2")
        print("Capital (MYR):", CAPITAL_RM)
        print("Max risk (MYR):",
              round(CAPITAL_RM * RISK_PERCENT, 2))

    except Exception as e:
        print(f"{symbol}: ERROR - {e}")


print("AI TRADING SCANNER - PHASE 2")
print("Historical market data / Paper trading")
print("Timestamp:",
      datetime.now(timezone.utc).isoformat())

for market, symbols in WATCHLIST.items():
    for symbol in symbols:
        analyze_stock(symbol, market)
