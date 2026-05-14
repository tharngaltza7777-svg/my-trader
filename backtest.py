import yfinance as yf
import pandas as pd

# --- CONFIGURATION ---
SYMBOL = "EURUSD=X" # စမ်းသပ်လိုသည့် pair
START_BALANCE = 5000 # အစပျိုးအရင်းအနှီး (AED)
TRADE_SIZE = 500     # တစ်ခါ Trade လျှင် သုံးမည့်ပမာဏ

def calculate_rsi(series, window=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=window-1, adjust=False).mean()
    ema_down = down.ewm(com=window-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

# ၁။ ဒေတာဆွဲယူခြင်း (ရက်ပေါင်း ၆၀ စာ ၁ မိနစ်ဒေတာ)
data = yf.download(SYMBOL, period="1mo", interval="5m")
data['RSI'] = calculate_rsi(data['Close'])

# ၂။ Backtesting Variables
balance = START_BALANCE
position = 0 # 0 = None, 1 = Buy, -1 = Sell
entry_price = 0
trades = []

# ၃။ Loop ပတ်ပြီး Strategy စစ်ဆေးခြင်း
for i in range(len(data)):
    rsi = data['RSI'].iloc[i]
    price = data['Close'].iloc[i]
    
    # Buy Logic (RSI < 42)
    if rsi < 42 and position == 0:
        position = 1
        entry_price = price
        trades.append({"Type": "BUY", "Price": price, "Time": data.index[i]})
        
    # Sell Logic (RSI > 58)
    elif rsi > 58 and position == 1:
        profit = (price - entry_price) * (TRADE_SIZE / entry_price)
        balance += profit
        position = 0
        trades.append({"Type": "EXIT BUY", "Price": price, "Profit": profit})

# ၄။ ရလဒ်ထုတ်ပြန်ခြင်း
print(f"--- {SYMBOL} Backtest Result ---")
print(f"Initial Balance: {START_BALANCE} AED")
print(f"Final Balance: {balance:.2f} AED")
print(f"Total Profit/Loss: {balance - START_BALANCE:.2f} AED")
print(f"Total Trades: {len(trades)}")
