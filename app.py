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

# ၁ မိနစ်တစ်ခါ Auto-refresh
st_autorefresh(interval=1 * 60 * 1000, key="ai_agent_with_report")

# Data Storage for Daily Report
if "history" not in st.session_state:
    st.session_state.history = []
if "daily_stats" not in st.session_state:
    st.session_state.daily_stats = {"Total": 0, "Buy": 0, "Sell": 0}

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
st.markdown(f"**Live Monitoring** | **Capital:** {TRADE_AED} AED")

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
        close_prices = data['Close'].squeeze()
        rsi_series = calculate_rsi(close_prices)
        current_price = float(close_prices.iloc[-1])
        current_rsi = float(rsi_series.iloc[-1])
        
        # Quantum Score Calculation
        momentum = float(close_prices.diff().iloc[-1])
        q_score = 0.5 + (0.05 if momentum > 0 else -0.05)

        # AI Agent Processing
        analysis_result = technical_analyst_agent(current_rsi)
        final_decision = decision_agent(analysis_result, q_score)

        # Dashboard UI
        c1, c2, c3 = st.columns(3)
        p_fmt = "{:.5f}" if "USD" in asset_label else "{:.2f}"
        c1.metric("Live Price", p_fmt.format(current_price))
        c2.metric("AI Analysis", analysis_result)
        c3.metric("RSI (14)", f"{current_rsi:.2f}")

        st.info(f"🧠 **AI Decision:** {final_decision}")

        # Notification & Stats Logging
        if final_decision in ["CONFIRMED_BUY", "CONFIRMED_SELL"]:
            h_key = f"v6_{ticker_symbol}_{final_decision}_{datetime.now().hour}"
            if h_key not in st.session_state:
                now = datetime.now().strftime("%H:%M:%S")
                trade_action = "BUY 🟢" if "BUY" in final_decision else "SELL 🔴"
                
                async def send_signal():
                    bot = Bot(token=TOKEN)
                    msg = (f"🤖 **AI SIGNAL**\nAsset: {asset_label}\n"
                           f"Action: {trade_action}\nPrice: {p_fmt.format(current_price)}")
                    await bot.send_message(chat_id=CHAT_ID, text=msg)

                asyncio.run(send_signal())
                
                # Update Daily Statistics
                st.session_state.history.append({"Pair": asset_label, "Time": now, "Action": trade_action, "Price": p_fmt.format(current_price)})
                st.session_state.daily_stats["Total"] += 1
                if "BUY" in trade_action: st.session_state.daily_stats["Buy"] += 1
                else: st.session_state.daily_stats["Sell"] += 1
                st.session_state[h_key] = True

    # --- DAILY REPORT SECTION ---
    st.divider()
    st.subheader("📊 Daily Trading Report")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Signals", st.session_state.daily_stats["Total"])
    col_b.metric("Buy Signals", st.session_state.daily_stats["Buy"])
    col_c.metric("Sell Signals", st.session_state.daily_stats["Sell"])

    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history).tail(10))
        
        # Report ပို့ရန် Button
        if st.button("Send Daily Report to Telegram"):
            async def send_report():
                bot = Bot(token=TOKEN)
                report_msg = (f"📋 **DAILY SUMMARY REPORT**\n"
                              f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
                              f"Total Signals: {st.session_state.daily_stats['Total']}\n"
                              f"Buy: {st.session_state.daily_stats['Buy']} | Sell: {st.session_state.daily_stats['Sell']}\n"
                              f"Estimated Volume: {st.session_state.daily_stats['Total'] * TRADE_AED} AED")
                await bot.send_message(chat_id=CHAT_ID, text=report_msg)
            asyncio.run(send_report())
            st.success("Daily Report ကို ပို့လိုက်ပါပြီဗျာ!")

except Exception as e:
    st.error(f"System Error: {e}")
