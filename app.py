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

# RSI ကို Library မလိုဘဲ ကိုယ်တိုင်တွက်ချက်သည့် Function
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

st.title("🤖 Master Auto-Pilot Trader V3")
st.info("စနစ်သည် ၃ မိနစ်တစ်ခါ ဈေးကွက်ကို အလိုအလျောက် စစ်ဆေးနေပါသည်")

try:
    # ဈေးနှုန်းဒေတာ ရယူခြင်း
    df = yf.download("BTC-USD", period="1d", interval="1m")
    
    if not df.empty:
        # RSI တွက်ခြင်း
        df['RSI'] = calculate_rsi(df['Close'])
        # Simple Moving Average တွက်ခြင်း
        df['SMA'] = df['Close'].rolling(window=20).mean()
        
        current_price = float(df['Close'].iloc[-1])
        current_rsi = float(df['RSI'].iloc[-1])
        sma_val = float(df['SMA'].iloc[-1])
        
        # Strategy Logic
        action = "WAIT"
        if current_rsi < 35 and current_price > sma_val:
            action = "BUY"
        elif current_rsi > 65 and current_price < sma_val:
            action = "SELL"

        # Dashboard Display
        c1, c2, c3 = st.columns(3)
        c1.metric("BTC Price", f"${current_price:,.2f}")
        c2.metric("RSI", f"{current_rsi:.2f}")
        c3.metric("Signal", action)

        # Telegram Signal Sending
        if action != "WAIT":
            if "last_action" not in st.session_state or st.session_state.last_action != action:
                async def send_msg():
                    bot = Bot(token=TOKEN)
                    text = f"🚨 **AUTO-PILOT ALERT**\n🪙 BTC/USD\n✨ Action: {action}\n💰 Price: ${current_price:,.2f}\n📈 RSI: {current_rsi:.2f}"
                    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
                
                asyncio.run(send_msg())
                st.session_state.last_action = action
                st.success("Signal ပို့ဆောင်ပြီးပါပြီ!")
        else:
            st.session_state.last_action = "WAIT"
            st.write("ဈေးကွက် အခြေအနေ စောင့်ကြည့်ဆဲ...")

except Exception as e:
    st.error(f"ခေတ္တစောင့်ဆိုင်းပေးပါ၊ Data ရယူနေဆဲဖြစ်သည်... ({e})")
