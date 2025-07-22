from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from voice_translator import translate_audio
import uvicorn

app = FastAPI()

# Permitir acceso desde tu frontend en Vercel
origins = [
    "https://voice-translator-project.vercel.app",  # tu frontend en Vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Asegura que solo este origen tenga acceso
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/translate")
async def translate(audio: UploadFile = File(...), target_language: str = Form(...)):
    try:
        translated_text, translated_audio_path = await translate_audio(audio, target_language)
        return {"text": translated_text, "audio_url": translated_audio_path}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
