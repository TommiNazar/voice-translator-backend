from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import os
import uuid
from pydub import AudioSegment
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS

app = FastAPI()

# ✅ Permitir peticiones desde Vercel y desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://voice-translator-project.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Montar carpeta estática para servir los audios traducidos
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Crear carpeta "static" si no existe
os.makedirs("static", exist_ok=True)

@app.post("/translate")
async def translate_audio(
    audio: UploadFile = File(...),
    target_language: str = Form(...)
):
    try:
        # ✅ Guardar archivo original
        audio_id = str(uuid.uuid4())
        webm_path = f"static/{audio_id}.webm"
        with open(webm_path, "wb") as f:
            f.write(await audio.read())

        # ✅ Convertir a .wav
        wav_path = f"static/{audio_id}.wav"
        sound = AudioSegment.from_file(webm_path)
        sound.export(wav_path, format="wav")

        # ✅ Transcribir con SpeechRecognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                transcription = recognizer.recognize_google(audio_data, language="es-AR")
            except Exception:
                transcription = "No se pudo transcribir"

        # ✅ Traducir con Google Translate
        translator = Translator()
        try:
            translation = translator.translate(transcription, dest=target_language).text
        except Exception:
            translation = "No se pudo traducir"

        # ✅ Generar audio traducido
        try:
            tts = gTTS(translation, lang=target_language)
            translated_audio_filename = f"audio_traducido_{audio_id}.mp3"
            translated_audio_path = f"static/{translated_audio_filename}"
            tts.save(translated_audio_path)

            # ✅ Ruta pública en Render (ajustar si cambia tu URL de backend)
            audio_url = f"https://voice-translator-backend-1n3i.onrender.com/static/{translated_audio_filename}"
        except Exception:
            audio_url = None

        return JSONResponse(content={
            "transcription": transcription,
            "translation": translation,
            "audio_url": audio_url
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "error": "Ocurrió un error interno en el servidor",
            "detail": str(e)
        })
