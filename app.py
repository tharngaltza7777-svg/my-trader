import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from telegram import Bot
from qiskit import QuantumCircuit
from qiskit_aer import Aer

# Telegram Credentials
TOKEN = "8140108107:AAH1AEOF1pZzYRNkDDm1v4ylvBHC-IcQIhM"
CHAT_ID = "8344079627"

def run_quantum_logic(rsi_value):
    qc = QuantumCircuit(1, 1)
    qc.ry((rsi_value/100)*3.14159, 0)
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
    with st.spinner("ဈေးနှုန်း ရယူနေပါသည်..."):
        try:
            # Yahoo Finance မှ BTC-USD ကို ယူခြင်း
            data = yf.download("BTC-USD", period="1d", interval="1m")
            if not data.empty:
                # .item() ထည့်ခြင်းဖြင့် Format Error ကို ဖြေရှင်းသည်
                price = data['Close'].iloc[-1].item() 
                
                # Quantum Analysis
                q_score = run_quantum_logic(50) 
                action = "BUY" if q_score > 0.52 else "SELL" if q_score < 0.48 else "WAIT"
                
                # Dashboard တွင် ပြသခြင်း
                st.metric(label="BTC/USD Price", value=f"${price:,.2f}")
                st.write(f"Quantum Probability: {q_score:.2%}")
                
                if action != "WAIT":
                    asyncio.run(send_signal("BTC/USD", action, price, q_score))
                    st.success(f"Signal ({action}) ကို Telegram သို့ ပို့လိုက်ပါပြီ!")
                else:
                    st.info("ဈေးကွက် အခြေအနေ စောင့်ကြည့်ဆဲ ဖြစ်ပါသည်။")
            else:
                st.error("ဈေးနှုန်း ရယူ၍ မရနိုင်သေးပါ။")
                
        except Exception as e:
            st.error(f"Error: {e}")
