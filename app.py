import streamlit as st
import yfinance as yf
import ccxt
import asyncio
from telegram import Bot
from qiskit import QuantumCircuit
from qiskit_aer import Aer

# --- CONFIGURATION ---
TOKEN = "8140108107:AAH1AEOF1pZzYRNkDDm1v4ylvBHC-IcQIhM"
CHAT_ID = "8344079627"

# Exchange API (Limit Order တင်ရန်အတွက် - ဥပမာ Bybit)
# စမ်းသပ်ရန်အတွက် API Key မပါဘဲ ရေးထားပါသည်၊ အမှန်တကယ်သုံးလျှင် Key ထည့်ရန် လိုပါမည်
exchange = ccxt.bybit({
    'apiKey': 'YOUR_BYBIT_API_KEY',
    'secret': 'YOUR_BYBIT_SECRET_KEY',
    'enableRateLimit': True,
})

def run_quantum_logic(rsi_value):
    qc = QuantumCircuit(1, 1)
    qc.ry((rsi_value/100)*3.14159, 0)
    qc.measure(0, 0)
    sim = Aer.get_backend('qasm_simulator')
    job = sim.run(qc, shots=1024)
    return job.result().get_counts().get('1', 0) / 1024.0

async def send_signal_and_order(symbol, action, price, q_score):
    bot = Bot(token=TOKEN)
    
    # ၁။ Limit Order တင်မည့် ဈေးနှုန်းသတ်မှတ်ခြင်း (ဥပမာ- လက်ရှိဈေးထက် ၀.၁% လျှော့ဝယ်ခြင်း)
    limit_price = price * 0.999 if action == "BUY" else price * 1.001
    
    # ၂။ Telegram သို့ အကြောင်းကြားစာပို့ခြင်း
    msg = (f"🚀 **MASTER SIGNAL & ORDER**\n"
           f"🪙 {symbol}\n"
           f"🎯 Action: {action}\n"
           f"💰 Current: ${price:,.2f}\n"
           f"📝 Limit Order: ${limit_price:,.2f}\n"
           f"📊 Q-Score: {q_score:.2%}")
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
    
    # ၃။ အော်ဒါ အမှန်တကယ် တင်ခြင်း (API Key ရှိမှ အလုပ်လုပ်မည်)
    # try:
    #     amount = 0.001 # စမ်းသပ်မည့် ပမာဏ
    #     if action == "BUY":
    #         exchange.create_limit_buy_order(symbol, amount, limit_price)
    #     elif action == "SELL":
    #         exchange.create_limit_sell_order(symbol, amount, limit_price)
    # except Exception as e:
    #     print(f"Order Error: {e}")

st.title("Myanmar Quantum Master Trader")

if st.button("ဈေးကွက်စစ်ဆေးပြီး အော်ဒါတင်မည်"):
    with st.spinner("Analyzing Market Data..."):
        try:
            data = yf.download("BTC-USD", period="1d", interval="1m")
            if not data.empty:
                price = data['Close'].iloc[-1].item()
                
                # Quantum Analysis
                q_score = run_quantum_logic(50) 
                action = "BUY" if q_score > 0.55 else "SELL" if q_score < 0.45 else "WAIT"
                
                st.metric(label="BTC/USD", value=f"${price:,.2f}")
                
                if action != "WAIT":
                    asyncio.run(send_signal_and_order("BTC/USDT", action, price, q_score))
                    st.success(f"Signal ပို့ပြီး {action} Limit Order ကို ပြင်ဆင်လိုက်ပါပြီ!")
                else:
                    st.info("Market Not Ready - No Order Placed.")
            else:
                st.error("Data fetch failed.")
        except Exception as e:
            st.error(f"Error: {e}")
