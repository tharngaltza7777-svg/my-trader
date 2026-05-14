import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from telegram import Bot
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- CONFIGURATION ---
TOKEN = "8797384581:AAHN2awLJgzsUPnJgOBr4WFBM2E-ysscUE4"
CHAT_ID = "8344079627"
TRADE_AED = 500

st_autorefresh(interval=1 * 60 * 1000, key="ai_agent_final_fix")

if "history" not in st.session_state:
    st.session_state.history = []

def technical_analyst_agent(rsi):
    if rsi < 42: return "BULLISH_SIGNAL"
    elif rsi > 58: return "BEARISH_SIGNAL"
    return "STABLE"

def decision_agent(signal, q_score):
    if signal == "BULLISH_SIGNAL" and q_score < 0.55: return "CONFIRMED_BUY"
    elif signal == "BEARISH_SIGNAL" and q_score > 0.45: return "CONFIRMED_SELL"
    return "HOLD"

def calculate_rsi(series, window=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=window-1, adjust=False).mean()
    ema_down = down.ewm(com=window-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

st.title("🤖 AI Agent Forex Master")
st.markdown(f"**Status:** System Fixed | **Capital:** {TRADE_AED} AED")

major_pairs = {
    "EUR/USD (Euro)": "EURUSD=X",
    "GBP/USD (Pound)": "GBPUSD=X",
    "USD/JPY (Yen)": "JPY=X",
    "Gold (XAU/USD)": "GC=F",
    "Bitcoin (BTC/USD)": "BTC-USD"
}
asset_label = st.selectbox("🎯 Target Pair", list(major_pairs.keys()))
ticker_symbol = major_pairs[asset_label]

try:
    data = yf.download(ticker_symbol, period="2d", interval="1m", progress=False)
    
    if not data.empty and len(data) > 15:
        # Error တက်စေသည့် Series ပြဿနာကို ဤနေရာတွင် ပြင်ဆင်ထားသည်
        close_prices = data['Close'].squeeze() 
        rsi_series = calculate_rsi(close_prices)
        
        current_price = float(close_prices.iloc[-1])
        current_rsi = float(rsi_series.iloc[-1])
        
        # Quantum Score Calculation
        momentum = float(close_prices.diff().iloc[-1])
        q_score = 0.5 + (0.05 if momentum > 0 else -0.05)

        # AI Agents Analysis
        analysis_result = technical_analyst_agent(current_rsi)
        final_decision = decision_agent(analysis_result, q_score)

        # UI Display
        col1, col2, col3 = st.columns(3)
        p_fmt = "{:.5f}" if "USD" in asset_label else "{:.2f}"
        col1.metric("Live Price", p_fmt.format(current_price))
        col2.metric("AI Analysis", analysis_result)
        col3.metric("RSI (14)", f"{current_rsi:.2f}")

        st.info(f"🧠 **AI Decision:** {final_decision}")

        # Notification
        if final_decision in ["CONFIRMED_BUY", "CONFIRMED_SELL"]:
            h_key = f"agent_v5_{ticker_symbol}_{final_decision}"
            if h_key not in st.session_state:
                now = datetime.now().strftime("%H:%M:%S")
                trade_action = "BUY 🟢" if "BUY" in final_decision else "SELL 🔴"
                
                async def send_agent_msg():
                    try:
                        bot = Bot(token=TOKEN)
                        msg = (f"🤖 **AI AGENT SIGNAL**\n\n"
                               f"Asset: {asset_label}\n"
                               f"Decision: {trade_action}\n"
                               f"Entry Price: {p_fmt.format(current_price)}\n"
                               f"Analysis: {analysis_result}")
                        await bot.send_message(chat_id=CHAT_ID, text=msg)
                    except: pass

                asyncio.run(send_agent_msg())
                st.session_state.history.append({"Pair": asset_label, "Time": now, "Action": trade_action})
                st.session_state[h_key] = True

        if st.session_state.history:
            st.divider()
            st.table(pd.DataFrame(st.session_state.history).tail(5))

except Exception as e:
    st.error(f"System Error: {e}")
