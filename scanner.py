
from datetime import datetime, timezone

# AI Trading Scanner - Phase 1
# Simulation only: no live market data yet.

CAPITAL = 250.00
MAX_RISK = CAPITAL * 0.02

def analyze_trade(symbol, market, entry, stop_loss, take_profit):
    risk_per_share = entry - stop_loss
    reward_per_share = take_profit - entry

    if risk_per_share <= 0 or reward_per_share <= 0:
        return {"symbol": symbol, "signal": "INVALID SETUP"}

    reward_ratio = reward_per_share / risk_per_share
    quantity = min(
        int(MAX_RISK / risk_per_share),
        int(CAPITAL / entry)
    )

    return {
        "symbol": symbol,
        "market": market,
        "signal": "PAPER SETUP" if reward_ratio >= 2 and quantity > 0 else "NO TRADE",
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "quantity": quantity,
        "risk_reward": round(reward_ratio, 2),
        "estimated_risk": round(quantity * risk_per_share, 2),
        "estimated_profit": round(quantity * reward_per_share, 2),
    }

# Fictional examples, NOT real stock prices.
examples = [
    ("US-DEMO", "US", 10.00, 9.50, 11.00),
    ("MY-DEMO", "MY", 1.00, 0.95, 1.10),
]

print("AI TRADING SCANNER - SIMULATION")
print("Timestamp:", datetime.now(timezone.utc).isoformat())
print("Capital: RM", CAPITAL)

for example in examples:
    print(analyze_trade(*example))
