from datetime import datetime, timezone
from pathlib import Path
import json
import math

import yfinance as yf
import pandas as pd

# AI Trading Scanner - Phase 3
# Historical prices, PAPER TRADING ONLY. No real orders are ever placed.
# Output: docs/data.json (read by the GitHub Pages dashboard docs/index.html)

CAPITAL_RM = 250.00
RISK_PERCENT = 0.02
MIN_RR = 2.0
STOP_PCT = 0.05     # illustrative stop 5% below price
TARGET_PCT = 0.10   # illustrative target 10% above price (1:2)
BURSA_LOT = 100     # Bursa Malaysia board lot size

# Example stocks from US and Bursa Malaysia
WATCHLIST = {
    "US": ["AAPL", "MSFT", "NVDA"],
    "MY": ["1155.KL", "1023.KL", "5347.KL"]
}

CURRENCY = {"US": "USD", "MY": "MYR"}
OUTPUT_FILE = Path("docs") / "data.json"


def r2(x):
    return None if x is None or not math.isfinite(x) else round(float(x), 2)


def calc_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False,
                        min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False,
                        min_periods=period).mean()
    if avg_loss.iloc[-1] == 0:
        return 100.0 if avg_gain.iloc[-1] > 0 else 50.0
    rs = avg_gain.iloc[-1] / avg_loss.iloc[-1]
    return float(100 - (100 / (1 + rs)))


def paper_plan(price, market):
    """Illustrative paper-trade plan. Only called for PAPER WATCHLIST."""
    stop = price * (1 - STOP_PCT)
    target = price * (1 + TARGET_PCT)
    plan = {
        "illustrative_stop": r2(stop),
        "illustrative_target": r2(target),
        "risk_reward": f"1:{MIN_RR:g}",
    }
    if market == "MY":
        max_risk = CAPITAL_RM * RISK_PERCENT
        risk_per_share = price - stop
        by_risk = math.floor(max_risk / risk_per_share)
        by_capital = math.floor(CAPITAL_RM / price)
        units = max(0, min(by_risk, by_capital))
        plan["paper_units"] = units
        plan["paper_cost_rm"] = r2(units * price)
        plan["paper_risk_rm"] = r2(units * risk_per_share)
        plan["below_one_lot"] = units < BURSA_LOT
    else:
        # USD prices: no position size without a verified USD/MYR rate.
        plan["paper_units"] = None
        plan["sizing_note"] = "Not sized: no verified USD/MYR rate"
    return plan


def analyze_stock(symbol, market):
    base = {"symbol": symbol, "market": market,
            "currency": CURRENCY[market]}
    try:
        df = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df.empty:
            return {**base, "error": "No data"}

        close = pd.to_numeric(df["Close"], errors="coerce").dropna()
        if len(close) < 55:
            return {**base, "error": "Insufficient data"}

        price = float(close.iloc[-1])
        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])
        rsi = calc_rsi(close)

        signal = "NO TRADE"
        if price > ma20 > ma50 and 50 <= rsi <= 70:
            signal = "PAPER WATCHLIST"

        result = {
            **base,
            "data_date": close.index[-1].strftime("%Y-%m-%d"),
            "price": r2(price),
            "sma20": r2(ma20),
            "sma50": r2(ma50),
            "rsi14": r2(rsi),
            "signal": signal,
            # NO TRADE -> no stop/target is produced at all
            "plan": paper_plan(price, market)
            if signal == "PAPER WATCHLIST" else None,
        }
        return result
    except Exception as e:
        return {**base, "error": str(e)[:200]}


def main():
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print("AI TRADING SCANNER - PHASE 3")
    print("Historical market data / Paper trading only")
    print("Timestamp:", generated_at)

    stocks = []
    for market, symbols in WATCHLIST.items():
        for symbol in symbols:
            row = analyze_stock(symbol, market)
            stocks.append(row)
            print("---------------------------")
            for k, v in row.items():
                print(f"{k}: {v}")

    payload = {
        "generated_at_utc": generated_at,
        "mode": "PAPER TRADING ONLY - historical data, no real orders",
        "capital_rm": CAPITAL_RM,
        "risk_percent": RISK_PERCENT * 100,
        "max_risk_rm": r2(CAPITAL_RM * RISK_PERCENT),
        "stocks": stocks,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
