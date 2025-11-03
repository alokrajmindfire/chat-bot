from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from google import genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="Gemini Q&A API", version="1.0")

origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "Welcome to chatbot!"}

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=req.question
        )
        return {"answer": response.text}
    except Exception as e:
        return {"error": str(e)}
