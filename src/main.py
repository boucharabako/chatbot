from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from mangum import Mangum
import json, boto3
from mistralai import Mistral


from .config import env_vars


from .utils import Utils

api_key = env_vars.MISTRAL_API_KEY
model = "mistral-small-latest"
client = Mistral(api_key=api_key)



@asynccontextmanager
async def app_lifespan(application: FastAPI):
    Utils.log_info("Starting the application")
    yield


app = FastAPI(
    title="ChatBot API",
    description="Chatbot API description",
    version="1.0.0",
    lifespan=app_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"msg": "Hello World"}


# @app.get("/chat")
# async def chat(question: str):
#     chat_response = client.chat.complete(
#         model=model,
#         messages=[
#             {
#                 "role": "user",
#                 "content": question,
#             },
#         ]
#     )
#     print(chat_response)
#     response = {
#         "id": {
#             "S": f"{chat_response.id}",
#         },
#         "question": {
#             "S": f"{question}",
#         },
#         "answer": {
#             "S": f"{chat_response.choices[0].message.content}",
#         }
#     }
#     Utils.insert_data(response)
#     return response


@app.get("/chat")
async def chat(request: Request, question: str):
    user_id = request.headers.get("X-User-ID", "inconnu")

    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": question,
            },
        ]
    )

    answer = chat_response.choices[0].message.content

    response = {
        "conversation_id": {"S": user_id},
        "message_id": {"S": str(uuid4())},
        "question": {"S": question},
        "answer": {"S": answer},
        "timestamp": {"S": Utils.get_timestamp()}
    }
    Utils.insert_data(response)

    return {
        "question": question,
        "answer": answer
    }

@app.get("/history")
async def get_history(request: Request):
    user_id = request.headers.get("X-User-ID", "inconnu")
    history = Utils.get_conversation_history(user_id)
    return {"history": history}


async def chats():
    # All chats
    return {}

handler = Mangum(app)