from fastapi import FastAPI, Request
import requests
import uvicorn

app = FastAPI()

# သင့်ရဲ့ New Telegram Bot Config
TOKEN = "8140108107:AAH1AEOF1pZzYRNkDDm1v4ylvBHC-IcQIhM"
CHAT_ID = "8344079627"

@app.get("/")
def home():
    return {"status": "AI Agent Webhook Server is Live and Active"}

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    try:
        # TradingView မှ ပို့လိုက်သော JSON data ကို လက်ခံခြင်း
        data = await request.json()
        
        pair = data.get("pair", "Unknown Pair")
        price = data.get("price", "0.00")
        action = data.get("action", "HOLD")
        rsi = data.get("rsi", "N/A")
        
        # RSI တန်ဖိုးကို ဒဿမ ၂ နေရာအဖြစ် ပြင်ဆင်ခြင်း
        try:
            rsi_val = f"{float(rsi):.2f}"
        except:
            rsi_val = str(rsi)
            
        # Telegram သို့ ပို့မည့် စာသားပုံစံ
        msg = (f"🚀 **INSTANT AI TRADING SIGNAL**\n\n"
               f"🎯 Asset: {pair}\n"
               f"⚡ Action: {action}\n"
               f"💵 Price: {price}\n"
               f"📊 RSI (14): {rsi_val}\n\n"
               f"🔒 Status: Execution Automated via GitHub Engine")
               
        # Telegram API သို့ တိုက်ရိုက် တင်ပို့ခြင်း
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload)
        
        return {"status": "success", "telegram_response": response.status_code}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
