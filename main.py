from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import Response
import json
import os
import uuid
import shutil
from utils.transcription import transcribe_audio
from utils.translation import translate_text
from utils.text_to_speech import text_to_speech

app = FastAPI()

@app.post("/translate")
async def translate_audio(
    audio: UploadFile = File(...),
    target_language: str = Form(...)
):
    try:
        # Guardar el archivo de audio en el sistema de archivos
        audio_id = str(uuid.uuid4())
        audio_path = f"temp_{audio_id}.webm"

        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # Transcribir el audio
        transcription = transcribe_audio(audio_path)

        # Traducir el texto transcripto
        translation = translate_text(transcription, target_language)

        # Convertir texto traducido a voz
        translated_audio_path = text_to_speech(translation, target_language)

        # Simular URL pública (en producción deberías subirlo a un storage real)
        audio_url = f"https://voice-translator-backend-1n3i.onrender.com/{translated_audio_path}"

        # CORS: devolvemos con encabezados manuales
        headers = {"Access-Control-Allow-Origin": "https://voice-translator-project.vercel.app"}

        return Response(
            content=json.dumps({
                "transcription": transcription,
                "translation": translation,
                "audio_url": audio_url
            }),
            media_type="application/json",
            headers=headers
        )

    except Exception as e:
        headers = {"Access-Control-Allow-Origin": "https://voice-translator-project.vercel.app"}

        return Response(
            content=json.dumps({
                "error": "Ocurrió un error interno en el servidor",
                "detail": str(e)
            }),
            media_type="application/json",
            status_code=500,
            headers=headers
        )
