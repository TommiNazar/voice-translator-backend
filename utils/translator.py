import uuid
import os
from gtts import gTTS
import whisper

model = whisper.load_model("base")

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]

def translate_text(text, target_language):
    # Devuelve el texto original (podés usar DeepL o Google Translate después)
    return text

def text_to_speech(text, lang_code):
    filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join("static/audio", filename)
    tts = gTTS(text=text, lang=lang_code)
    tts.save(output_path)
    return output_path
