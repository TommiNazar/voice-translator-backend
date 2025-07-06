from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
from pydub import AudioSegment
import speech_recognition as sr
from googletrans import Translator
import tempfile

app = FastAPI()

# Permitir solicitudes desde tu frontend en Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://voice-translator-project.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


# Carpeta para guardar archivos temporales
os.makedirs("static", exist_ok=True)

@app.post("/translate")
async def translate_audio(
    audio: UploadFile = File(...),
    target_language: str = Form(...)
):
    # Guardar el archivo recibido
    audio_id = str(uuid.uuid4())
    audio_path = f"static/{audio_id}.webm"
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    # Convertir de .webm a .wav usando pydub (requiere ffmpeg instalado)
    try:
        sound = AudioSegment.from_file(audio_path)
        wav_path = f"static/{audio_id}.wav"
        sound.export(wav_path, format="wav")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Error al convertir el audio", "detail": str(e)}
        )

    # Transcripción
    recognizer = sr.Recognizer()
    transcription = ""
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data, language="es-AR")
    except Exception as e:
        transcription = "No se pudo transcribir"

    # Traducción
    translator = Translator()
    try:
        translation = translator.translate(transcription, dest=target_language).text
    except Exception as e:
        translation = "No se pudo traducir"

    # Texto traducido a voz (audio)
    try:
        tts = gTTS(translation, lang=target_language)
        translated_audio_path = f"static/audio_traducido_{audio_id}.mp3"
        tts.save(translated_audio_path)
        audio_url = f"http://localhost:8000/{translated_audio_path}"
    except Exception as e:
        audio_url = None

    return JSONResponse(
        content={
            "transcription": transcription,
            "translation": translation,
            "audio_url": audio_url,
        }
    )
