from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="Gemini Q&A API", version="1.0")

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "Welcome to Gemini Q&A API!"}

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
