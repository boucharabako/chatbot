import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL", "http://localhost:8000/chat")

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    message = data.get("message")
    if not message:
        return JSONResponse(status_code=200, content={"message": "No message"})

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if not text:
        return JSONResponse(status_code=200, content={"message": "No text"})

    # Appelle l’API FastAPI pour obtenir la réponse
    try:
        response = requests.get(BACKEND_CHAT_URL, params={"question": text})
        response.raise_for_status()
        bot_response = response.json().get("answer", {}).get("S", "Je n'ai pas compris.")
    except Exception as e:
        bot_response = f"Erreur : {str(e)}"

    # Répondre via Telegram
    requests.post(
        f"{BOT_API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": bot_response},
    )

    return JSONResponse(status_code=200, content={"message": "ok"})
