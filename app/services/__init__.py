import assemblyai as aai
from config import ASSEMBLYAI_KEY

aai.settings.api_key = ASSEMBLYAI_KEY
config = aai.TranscriptionConfig(language_code='hi')

transcriber = aai.Transcriber(config=config)

def voice_to_text_converter(audio_file):
    transcript = transcriber.transcribe(audio_file)
    return transcript.text
