import streamlit as st
import pandas as pd
import ccxt
import numpy as np
import asyncio
from telegram import Bot
from qiskit import QuantumCircuit
from qiskit_aer import Aer

# Telegram Credentials
TOKEN = "8140108107:AAH1AEOF1pZzYRNkDDm1v4ylvBHC-IcQIhM"
CHAT_ID = "8344079627"

def run_quantum_logic(rsi):
    qc = QuantumCircuit(1, 1)
    qc.ry((rsi/100)*3.14159, 0)
    qc.measure(0, 0)
    sim = Aer.get_backend('qasm_simulator')
    job = sim.run(qc, shots=1024)
    return job.result().get_counts().get('1', 0) / 1024.0

async def send_signal(symbol, action, price, q_score):
    bot = Bot(token=TOKEN)
    msg = f"🚀 **QUANTUM SIGNAL**\n🪙 {symbol}\n🎯 {action}\n💰 ${price:,.2f}\n📊 Score: {q_score:.2%}"
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

st.title("Myanmar Quantum Trader")
if st.button("ဈေးကွက်စစ်ဆေးမည်"):
    with st.spinner("Analyzing..."):
        ex = ccxt.binance({'options': {'defaultType': 'future'}})
        data = ex.fetch_ohlcv("XAU/USDT", timeframe='1h', limit=2)
        price = data[-1][4]
        q_score = run_quantum_logic(50)
        action = "BUY" if q_score > 0.55 else "SELL" if q_score < 0.45 else "WAIT"
        st.write(f"လက်ရှိရွှေဈေး: ${price}")
        if action != "WAIT":
            asyncio.run(send_signal("GOLD", action, price, q_score))
            st.success("Telegram ကို Signal ပို့လိုက်ပါပြီ!")
