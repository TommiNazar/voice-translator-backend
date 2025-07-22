from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydub import AudioSegment
import os
import uuid
from utils.translator import transcribe_audio, translate_text, text_to_speech

app = FastAPI()

# CORS para Vercel + local
origins = [
    "http://localhost:3000",
    "https://voice-translator-project.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "static/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/translate")
async def translate_audio(audio: UploadFile = File(...), target_language: str = Form(...)):
    try:
        # Guardar el archivo temporal
        file_id = str(uuid.uuid4())
        audio_path = os.path.join(UPLOAD_DIR, f"{file_id}.webm")

        with open(audio_path, "wb") as f:
            f.write(await audio.read())

        # Convertir de .webm a .wav
        sound = AudioSegment.from_file(audio_path)
        wav_path = os.path.join(UPLOAD_DIR, f"{file_id}.wav")
        sound.export(wav_path, format="wav")

        # Transcripción y traducción
        text = transcribe_audio(wav_path)
        translated_text = translate_text(text, target_language)
        translated_audio_path = text_to_speech(translated_text, target_language)

        return {
            "original_text": text,
            "translated_text": translated_text,
            "translated_audio_url": f"/static/audio/{os.path.basename(translated_audio_path)}"
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
def root():
    return {"message": "Backend operativo 🎙️"}
