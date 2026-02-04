import os
import json
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# 1. API KEYS (Updated with your provided key)
GEMINI_API_KEY = "AIzaSyCRymXiBx8iKSOU5jRSF5SZjPWoG9cMxjQ"
VALID_API_KEY = "MY_SCAM_PROTECT_2026"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class ScamRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"status": "online", "message": "Scam Detection System is running"}

@app.post("/v1/detect")
async def detect_scam(request: ScamRequest, x_api_key: str = Header(None)):
    # Verify the custom API key for security
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    prompt = (
        f"Analyze this message for scam risk: {request.message}. "
        "Return ONLY a raw JSON object with these keys: "
        "'risk_percentage' (int), 'is_scam' (bool), 'honeypot_reply' (str)."
    )

    try:
        response = model.generate_content(prompt)
        # Clean the response in case Gemini adds markdown formatting
        clean_text = response.text.strip().replace('```json', '').replace('```', '')
        data = json.loads(clean_text)
        
        risk = data.get("risk_percentage", 0)
        
        # Risk Logic for the final message
        if risk >= 80:
            msg = f"HIGH RISK ({risk}%): Consult higher authorities immediately!"
        elif risk >= 40:
            msg = f"MEDIUM RISK ({risk}%): Be careful and suspicious."
        else:
            msg = "SAFE: No scam detected."

        return {
            "risk_score": f"{risk}%",
            "security_alert": msg,
            "honeypot_action": data.get("honeypot_reply") if risk >= 40 else "None"
        }
    except Exception as e:
        return {"error": "Processing failed", "details": str(e)}

# Essential for cloud deployment (Render/Railway)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)