import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
import time
from telegram import Bot
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
TOKEN = "8140108107:AAH1AEOF1pZzYRNkDDm1v4ylvBHC-IcQIhM"
CHAT_ID = "8344079627"

# ၃ မိနစ်တစ်ခါ Auto-refresh လုပ်ခိုင်းခြင်း
st_autorefresh(interval=3 * 60 * 1000, key="bot_loop")

# RSI တွက်ချက်သည့် Function (Exponential Weighted Moving Average ကိုသုံး၍ ပိုမိုတိကျစေသည်)
def calculate_rsi(series, window=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=window-1, adjust=False).mean()
    ema_down = down.ewm(com=window-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

st.title("🤖 Master Auto-Pilot Trader V3")

# ဒေတာ ရယူရန် ကြိုးစားခြင်း (Retry Logic ပါဝင်သည်)
def fetch_data():
    for i in range(3): # ၃ ကြိမ်အထိ ပြန်ကြိုးစားမည်
        try:
            df = yf.download("BTC-USD", period="5d", interval="1m", progress=False)
            if not df.empty and len(df) > 20:
                return df
        except:
            time.sleep(2) # Error တက်လျှင် ၂ စက္ကန့်စောင့်ပြီး ပြန်ကြိုးစားမည်
    return pd.DataFrame()

df = fetch_data()

if not df.empty:
    # Technical Indicators တွက်ချက်ခြင်း
    df['RSI'] = calculate_rsi(df['Close'])
    df['SMA'] = df['Close'].rolling(window=20).mean()
    
    current_price = float(df['Close'].iloc[-1])
    current_rsi = float(df['RSI'].iloc[-1])
    sma_val = float(df['SMA'].iloc[-1])
    
    # Strategy Logic
    action = "WAIT"
    if current_rsi < 35: action = "BUY"
    elif current_rsi > 65: action = "SELL"

    # Dashboard ပေါ်တွင် ပြသခြင်း
    c1, c2, c3 = st.columns(3)
    c1.metric("BTC Price", f"${current_price:,.2f}")
    c2.metric("RSI (14)", f"{current_rsi:.2f}")
    c3.metric("Action", action)

    # Telegram သို့ Signal ပို့ခြင်း
    if action != "WAIT":
        if "last_action" not in st.session_state or st.session_state.last_action != action:
            async def send_msg():
                bot = Bot(token=TOKEN)
                text = f"🚀 **STRATEGY ALERT**\n🎯 Action: {action}\n💰 Price: ${current_price:,.2f}\n📈 RSI: {current_rsi:.2f}"
                await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
            
            asyncio.run(send_msg())
            st.session_state.last_action = action
            st.success("Signal အသစ်ကို Telegram သို့ ပို့လိုက်ပါပြီ!")
    else:
        st.session_state.last_action = "WAIT"
        st.info("ဈေးကွက်ကို စောင့်ကြည့်နေပါသည်...")
else:
    st.warning("ဒေတာအသစ် ရယူနေဆဲ ဖြစ်ပါသည်။ ခဏစောင့်ပေးပါ...")
