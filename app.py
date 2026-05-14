import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from telegram import Bot
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
TOKEN = "8140108107:AAH1AEOF1pZzYRNkDDm1v4ylvBHC-IcQIhM"
CHAT_ID = "8344079627"

# ၃ မိနစ်တစ်ခါ Auto-refresh
st_autorefresh(interval=3 * 60 * 1000, key="bot_loop")

def calculate_rsi(series, window=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=window-1, adjust=False).mean()
    ema_down = down.ewm(com=window-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

st.title("🤖 Master Auto-Pilot Trader V3")

try:
    # ပိုမိုခိုင်မာသော ဒေတာရယူမှုပုံစံ
    ticker = yf.Ticker("BTC-USD")
    df = ticker.history(period="5d", interval="1m")
    
    if not df.empty and len(df) > 20:
        # RSI နှင့် SMA တွက်ချက်ခြင်း
        df['RSI'] = calculate_rsi(df['Close'])
        df['SMA'] = df['Close'].rolling(window=20).mean()
        
        # ဈေးနှုန်းများကို ပိုမိုစိတ်ချရသော နည်းလမ်းဖြင့် ယူခြင်း
        current_price = float(df['Close'].values[-1])
        current_rsi = float(df['RSI'].values[-1])
        sma_val = float(df['SMA'].values[-1])
        
        # Strategy Logic
        action = "WAIT"
        if current_rsi < 35: action = "BUY"
        elif current_rsi > 65: action = "SELL"

        # Display
        col1, col2, col3 = st.columns(3)
        col1.metric("BTC Price", f"${current_price:,.2f}")
        col2.metric("RSI", f"{current_rsi:.2f}")
        col3.metric("Signal", action)

        if action != "WAIT":
            if "last_action" not in st.session_state or st.session_state.last_action != action:
                async def send_msg():
                    bot = Bot(token=TOKEN)
                    text = f"🚀 **STRATEGY ALERT**\n🎯 Action: {action}\n💰 Price: ${current_price:,.2f}\n📈 RSI: {current_rsi:.2f}"
                    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
                
                asyncio.run(send_msg())
                st.session_state.last_action = action
                st.success("Signal ပို့ဆောင်ပြီးပါပြီ!")
        else:
            st.session_state.last_action = "WAIT"
            st.info("ဈေးကွက်ကို စောင့်ကြည့်နေပါသည်...")
    else:
        st.warning("ဒေတာအသစ် ရယူနေဆဲ ဖြစ်ပါသည်။")

except Exception as e:
    st.error(f"System Error: {e}")
