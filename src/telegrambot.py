import os
import httpx
from fastapi import FastAPI, Request, APIRouter 
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
BACKEND_CHAT_URL = os.getenv(
    "BACKEND_CHAT_URL",
    os.getenv("AWS_BACKEND_CHAT_URL") if os.getenv("AWS_EXECUTION_ENV") else "http://localhost:8080/chat"
)

app = FastAPI()

@router.post("/webhook")
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
        async with httpx.AsyncClient() as client:
            response = await client.get(BACKEND_CHAT_URL, params={"question": text})
            response.raise_for_status()
            # bot_response = response.json().get("answer", {}).get("S", "Je n'ai pas compris.")
            json_response = response.json()
            answer = json_response.get("answer")

            if isinstance(answer, dict):  
               bot_response = answer.get("S", "Je n'ai pas compris.")
            else:  
               bot_response = answer or "Je n'ai pas compris."
    except Exception as e:
        bot_response = f"Erreur : {str(e)}"

    # Répondre via Telegram (asynchrone)
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{BOT_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": bot_response},
        )

    return JSONResponse(status_code=200, content={"message": "ok"})
