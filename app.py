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

# Session State ထဲမှာ Signal History ကို သိမ်းရန်
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

st.title("🤖 Master Auto-Pilot & Daily Tracker")

try:
    ticker = yf.Ticker("BTC-USD")
    df = ticker.history(period="5d", interval="1m")
    
    if not df.empty and len(df) > 20:
        df['RSI'] = calculate_rsi(df['Close'])
        df['SMA'] = df['Close'].rolling(window=20).mean()
        
        current_price = float(df['Close'].values[-1])
        current_rsi = float(df['RSI'].values[-1])
        
        action = "WAIT"
        if current_rsi < 35: action = "BUY"
        elif current_rsi > 65: action = "SELL"

        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("BTC Price", f"${current_price:,.2f}")
        col2.metric("RSI", f"{current_rsi:.2f}")
        col3.metric("Current Signal", action)

        # Signal တွေ့လျှင် သိမ်းဆည်းပြီး Telegram ပို့ခြင်း
        if action != "WAIT":
            if "last_action" not in st.session_state or st.session_state.last_action != action:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # History ထဲသို့ ထည့်ခြင်း
                st.session_state.history.append({"Time": now, "Action": action, "Price": current_price})
                
                async def send_msg():
                    bot = Bot(token=TOKEN)
                    text = f"🚨 **AUTO ALERT**\n🎯 Action: {action}\n💰 Price: ${current_price:,.2f}\n⏰ Time: {now}"
                    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
                
                asyncio.run(send_msg())
                st.session_state.last_action = action
        else:
            st.session_state.last_action = "WAIT"

        # --- Daily Orders Win/Loss Section ---
        st.subheader("📊 Daily Order History")
        if st.session_state.history:
            history_df = pd.DataFrame(st.session_state.history)
            st.table(history_df.tail(10)) # နောက်ဆုံး Signal ၁၀ ခုကို ပြခြင်း
            
            # Win/Loss တွက်ချက်ရန် ခလုတ် (Manual update for result)
            st.info("မှတ်ချက်: အမြတ်/အရှုံးကို လက်ရှိဈေးနှုန်းနှင့် နှိုင်းယှဉ်တွက်ချက်ထားခြင်း ဖြစ်သည်။")
        else:
            st.write("ယနေ့အတွက် Signal မရှိသေးပါ။")

except Exception as e:
    st.error(f"System Error: {e}")
