import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from telegram import Bot
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- CONFIGURATION ---
TOKEN = "8140108107:AAH1AEOF1pZzYRNkDDm1v4ylvBHC-IcQIhM"
CHAT_ID = "8344079627"

st_autorefresh(interval=3 * 60 * 1000, key="bot_loop")

if "history" not in st.session_state:
    st.session_state.history = []

def calculate_rsi(series, window=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=window-1, adjust=False).mean()
    ema_down = down.ewm(com=window-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

st.title("🤖 Multi-Asset Auto-Pilot Trader")

# --- ASSET SELECTION ---
# Commodities နှင့် Crypto တွဲဖက်ပေးထားခြင်း
asset_choice = st.selectbox("ကြည့်ရှုမည့် Pair ကို ရွေးချယ်ပါ", 
    ["BTC-USD", "GC=F (Gold)", "SI=F (Silver)", "CL=F (Crude Oil)", "ETH-USD"])

# yfinance အတွက် Symbol ပြန်ညှိခြင်း
ticker_symbol = asset_choice.split(" ")[0]

try:
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="5d", interval="1m")
    
    if not df.empty and len(df) > 20:
        df['RSI'] = calculate_rsi(df['Close'])
        
        current_price = float(df['Close'].values[-1])
        current_rsi = float(df['RSI'].values[-1])
        
        action = "WAIT"
        if current_rsi < 35: action = "BUY"
        elif current_rsi > 65: action = "SELL"

        # Display Metrics
        st.subheader(f"📊 {asset_choice} Live Status")
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${current_price:,.2f}")
        col2.metric("RSI (14)", f"{current_rsi:.2f}")
        col3.metric("Signal", action)

        # Signal Logic & Telegram
        if action != "WAIT":
            # Signal အသစ်ဖြစ်မှ ပို့ရန် (Pair အလိုက်ခွဲသိမ်းရန်)
            history_key = f"last_{ticker_symbol}"
            if history_key not in st.session_state or st.session_state[history_key] != action:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.history.append({"Asset": ticker_symbol, "Time": now, "Action": action, "Price": current_price})
                
                async def send_msg():
                    bot = Bot(token=TOKEN)
                    text = f"🚨 **ASSET ALERT: {ticker_symbol}**\n🎯 Action: {action}\n💰 Price: ${current_price:,.2f}\n📈 RSI: {current_rsi:.2f}"
                    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
                
                asyncio.run(send_msg())
                st.session_state[history_key] = action
        
        # Daily History Table
        st.subheader("📅 Order History (All Assets)")
        if st.session_state.history:
            st.table(pd.DataFrame(st.session_state.history).tail(10))
        else:
            st.write("ယနေ့အတွက် Signal မရှိသေးပါ။")

except Exception as e:
    st.warning("ဒေတာ ရယူရန် ကြိုးစားနေဆဲ ဖြစ်ပါသည်။")
