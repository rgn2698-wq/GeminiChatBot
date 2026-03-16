from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = FastAPI()

# 개발중이라 일단 전체 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent"

class Message(BaseModel):
    role: str
    parts: list[dict]

class ChatRequest(BaseModel):
    history: list[Message]


@app.post("/chat")
def chat(req: ChatRequest):
    if not GEMINI_API_KEY:
        return {"error": "API 키가 없습니다. .env 파일을 확인하세요."}

    # history를 그대로 gemini에 넘김
    contents = [{"role": m.role, "parts": m.parts} for m in req.history]

    res = requests.post(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        json={"contents": contents}
    )

    data = res.json()

    # 오류나면 그냥 오류 내용 반환
    if res.status_code != 200:
        return {"error": data.get("error", {}).get("message", "알 수 없는 오류")}

    reply = data["candidates"][0]["content"]["parts"][0]["text"]
    return {"reply": reply}
