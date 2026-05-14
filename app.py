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
TRADE_AED = 500  # 500 AED Fixed Trade

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

st.title("🤖 AI Trade Analyst & Forecaster")

# Asset Selection
asset_choice = st.selectbox("Pair ကို ရွေးချယ်ပါ", ["BTC-USD", "GC=F (Gold)", "CL=F (Crude Oil)"])
ticker_symbol = asset_choice.split(" ")[0]

try:
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="5d", interval="1m")
    
    if not df.empty and len(df) > 20:
        df['RSI'] = calculate_rsi(df['Close'])
        current_price = float(df['Close'].values[-1])
        current_rsi = float(df['RSI'].values[-1])
        
        # --- Live Signal Logic ---
        action = "WAIT"
        if current_rsi < 35: action = "BUY"
        elif current_rsi > 65: action = "SELL"

        # --- NEXT DAY FORECAST LOGIC ---
        # RSI ရဲ့ အတက်အကျ Trend ကို ကြည့်ပြီး ခန့်မှန်းခြင်း
        rsi_change = current_rsi - float(df['RSI'].iloc[-5]) 
        forecast = "Neutral"
        if current_rsi < 45 and rsi_change > 0:
            forecast = "Potential BUY Opportunity"
        elif current_rsi > 55 and rsi_change < 0:
            forecast = "Potential SELL Opportunity"
        else:
            forecast = "Sideways - Wait for clear signal"

        # Dashboard Display
        st.subheader(f"📊 {asset_choice} Analysis")
        m1, m2, m3 = st.columns(3)
        m1.metric("Current Price", f"${current_price:,.2f}")
        m2.metric("RSI (14)", f"{current_rsi:.2f}")
        m3.metric("Live Signal", action)

        # Forecast Section
        st.info(f"🔮 **Next Session Forecast:** {forecast}")
        st.write(f"ခန့်မှန်းချက်အရ နောက်တစ်ကြိမ်တွင် **{TRADE_AED} AED** ဖိုး Trade ရန် အသင့်ပြင်ထားနိုင်ပါသည်။")

        # Telegram Logic (Signal ရှိမှ ပို့မည်)
        if action != "WAIT":
            history_key = f"last_{ticker_symbol}"
            if history_key not in st.session_state or st.session_state[history_key] != action:
                now = datetime.now().strftime("%H:%M:%S")
                st.session_state.history.append({"Asset": ticker_symbol, "Time": now, "Action": action, "Price": current_price})
                
                async def send_msg():
                    bot = Bot(token=TOKEN)
                    msg = (f"🚀 **LIVE SIGNAL: {ticker_symbol}**\nAction: {action}\n"
                           f"Price: ${current_price:,.2f}\nTrade: {TRADE_AED} AED\nForecast: {forecast}")
                    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
                
                asyncio.run(send_msg())
                st.session_state[history_key] = action

        # Analysis Table
        st.divider()
        st.subheader("📋 Trade Logs & Daily History")
        if st.session_state.history:
            st.table(pd.DataFrame(st.session_state.history).tail(5))
        else:
            st.write("ယနေ့အတွက် Signal မရှိသေးပါ။")

except Exception as e:
    st.warning("ဒေတာများ စစ်ဆေးနေဆဲဖြစ်ပါသည်။")
