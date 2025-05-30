from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import whisper
from gtts import gTTS
import requests
from fastapi import Form
import uuid
import os

app = FastAPI()

# Load Whisper model (base model)
#model = whisper.load_model("base")
@app.post("/speak")
async def voice_to_summary(file: UploadFile = File(...)):
    return {"error": "Voice-based input is disabled on Render to save memory. Please use /speak-text instead."}

@app.get("/")
def root():
    return {"message": "Voice Agent is live. Use POST /speak"}

@app.post("/speak-text")
def speak_text(summary: str = Form(...)):
    try:
        filename = f"response_{uuid.uuid4()}.mp3"
        tts = gTTS(text=summary)
        tts.save(filename)
        return FileResponse(filename, media_type="audio/mpeg", filename="response.mp3")
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/speak")
async def voice_to_summary(file: UploadFile = File(...)):
    # Save uploaded file
    filename = f"input_{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(await file.read())

    # Transcribe audio to text
    result = model.transcribe(filename)
    transcript = result["text"]

    # Send transcript to orchestrator (as a mock question)
    response = requests.get("https://finance-assistant2-orchestrator-production.up.railway.app/market-summary")
    summary = response.json().get("summary", "Sorry, I couldn't generate a summary.")

    # Convert summary to audio
    output_filename = f"response_{uuid.uuid4()}.mp3"
    tts = gTTS(text=summary)
    tts.save(output_filename)

    # Cleanup input
    os.remove(filename)

    return FileResponse(output_filename, media_type="audio/mpeg", filename="response.mp3")
