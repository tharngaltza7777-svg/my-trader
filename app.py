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
    with st.spinner("ဈေးကွက်ကို လေ့လာနေပါသည်..."):
        try:
            # Binance အစား Bybit ကို အသုံးပြုထားပါသည် (Location error ကင်းဝေးစေရန်)
            ex = ccxt.bybit()
            # BTC/USDT ဈေးနှုန်းကို ရယူခြင်း
            ticker = ex.fetch_ticker("BTC/USDT")
            price = ticker['last']
            
            # Quantum Logic တွက်ချက်ခြင်း
            q_score = run_quantum_logic(50)
            action = "BUY" if q_score > 0.55 else "SELL" if q_score < 0.45 else "WAIT"
            
            st.metric(label="BTC Price", value=f"${price:,.2f}")
            st.write(f"Quantum Probability Score: {q_score:.2%}")
            
            if action != "WAIT":
                asyncio.run(send_signal("BTC", action, price, q_score))
                st.success(f"Signal ({action}) ကို Telegram သို့ ပို့ဆောင်ပြီးပါပြီ!")
            else:
                st.warning("ဈေးကွက်က တန့်နေသဖြင့် Signal မထုတ်ပေးသေးပါ။")
                
        except Exception as e:
            st.error(f"ချိတ်ဆက်မှု အဆင်မပြေပါ: {e}")
