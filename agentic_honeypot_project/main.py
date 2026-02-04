import os
import json
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# --- CONFIGURATION ---
# Your provided Gemini API Key
GEMINI_API_KEY = "AIzaSyCRymXiBx8iKSOU5jRSF5SZjPWoG9cMxjQ"

# Your custom password for the judges
VALID_API_KEY = "MY_SCAM_PROTECT_2026"

# Initialize Google AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- DATA MODELS ---
class ScamRequest(BaseModel):
    message: str

# --- HEALTH CHECK ---
@app.get("/")
async def health_check():
    return {"status": "online", "message": "Agentic Honeypot is live!"}

# --- DETECTION ENDPOINT ---
@app.post("/v1/detect")
async def detect_scam(request: ScamRequest, x_api_key: str = Header(None)):
    # 1. Authorization Check
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key provided in header.")

    # 2. AI Prompt Logic
    prompt = f"""
    Analyze the following message for scam risk: "{request.message}"
    
    Return a JSON object with:
    1. "risk_percentage": (Integer 0-100)
    2. "is_scam": (Boolean)
    3. "honeypot_reply": (A response to trick a scammer into giving bank/IP info)
    
    Format example: {{"risk_percentage": 90, "is_scam": true, "honeypot_reply": "I'