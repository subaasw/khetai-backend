from pathlib import Path
import assemblyai as aai
from config import ASSEMBLYAI_KEY, BASE_UPLOAD_DIR

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

aai.settings.api_key = ASSEMBLYAI_KEY
config = aai.TranscriptionConfig(language_code='hi')

transcriber = aai.Transcriber(config=config)

async def voice_to_text_converter(audio_file):
    full_path = BASE_UPLOAD_DIR.cwd() / audio_file
    transcript = transcriber.transcribe(str(full_path))
    return transcript.text
