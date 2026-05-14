import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import asyncio
from telegram import Bot
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
TOKEN = "8140108107:AAH1AEOF1pZzYRNkDDm1v4ylvBHC-IcQIhM"
CHAT_ID = "8344079627"

# ၃ မိနစ်တစ်ခါ အလိုအလျောက် Refresh လုပ်ခိုင်းခြင်း (3 * 60 * 1000ms)
st_autorefresh(interval=3 * 60 * 1000, key="bot_loop")

def run_quantum_logic(rsi_value, ma_trend):
    qc = QuantumCircuit(1, 1)
    theta = (rsi_value / 100) * np.pi
    if ma_trend > 0: theta -= 0.2
    qc.ry(theta, 0)
    qc.measure(0, 0)
    sim = Aer.get_backend('qasm_simulator')
    job = sim.run(qc, shots=1024)
    return job.result().get_counts().get('1', 0) / 1024.0

async def send_instant_signal(symbol, action, price, rsi, q_score):
    bot = Bot(token=TOKEN)
    msg = (f"🚨 **INSTANT QUANTUM ALERT**\n"
           f"🪙 {symbol} | ✨ Action: **{action}**\n"
           f"💰 Price: ${price:,.2f}\n"
           f"📈 RSI: {rsi:.2f}\n"
           f"🔮 Q-Score: {q_score:.2%}\n"
           f"⏰ Time: Auto-detected")
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

st.title("🤖 Master Auto-Pilot Trader")
st.info("စနစ်သည် ၃ မိနစ်တစ်ခါ ဈေးကွက်ကို အလိုအလျောက် စစ်ဆေးနေပါသည်။")

# Analysis Logic (Auto-run on refresh)
try:
    df = yf.download("BTC-USD", period="1d", interval="1m")
    if not df.empty:
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['SMA'] = ta.sma(df['Close'], length=20)
        
        current_price = df['Close'].iloc[-1].item()
        current_rsi = df['RSI'].iloc[-1].item()
        ma_trend = 1 if current_price > df['SMA'].iloc[-1] else -1
        
        q_score = run_quantum_logic(current_rsi, ma_trend)
        
        # Strategy Logic
        if current_rsi < 35 and q_score > 0.55:
            action = "BUY"
        elif current_rsi > 65 and q_score < 0.45:
            action = "SELL"
        else:
            action = "WAIT"
        
        # Display Current Status
        c1, c2, c3 = st.columns(3)
        c1.metric("BTC", f"${current_price:,.2f}")
        c2.metric("RSI", f"{current_rsi:.1f}")
        c3.metric("Action", action)
        
        # Signal တွေ့လျှင် ချက်ခြင်းပို့ခြင်း
        if action != "WAIT":
            # Session State ကိုသုံးပြီး Signal တစ်ခုတည်းကို ထပ်ခါတလဲလဲ မပို့အောင် ထိန်းခြင်း
            if "last_action" not in st.session_state or st.session_state.last_action != action:
                asyncio.run(send_instant_signal("BTC/USD", action, current_price, current_rsi, q_score))
                st.session_state.last_action = action
                st.success(f"Signal အသစ်ကို Telegram သို့ ပို့လိုက်ပါပြီ!")
            else:
                st.write("Signal အဟောင်းအတိုင်း ဖြစ်နေသဖြင့် ထပ်မပို့တော့ပါ။")
        else:
            st.write("ဈေးကွက်အခြေအနေကို စောင့်ကြည့်နေပါသည်...")
            st.session_state.last_action = "WAIT"

except Exception as e:
    st.error(f"System Error: {e}")
