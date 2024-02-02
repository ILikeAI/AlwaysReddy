import openai
from pydub import AudioSegment
import os
from dotenv import load_dotenv
from config import AUDIO_FILE_DIR

# Load .env file if present
load_dotenv()

# Fetch API keys from .env file or environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

def transcribe_audio(file_path):
    client = openai.OpenAI(api_key=openai_api_key)
    audio = AudioSegment.from_file(f"{AUDIO_FILE_DIR}/{file_path}")

    # Define the chunk size (10 minutes in milliseconds)
    chunk_size = 10 * 60 * 1000

    # Calculate the number of chunks
    num_chunks = len(audio) // chunk_size + 1

    transcript = ""

    # Check the size of the file
    file_size = os.path.getsize(f"{AUDIO_FILE_DIR}/{file_path}")

    # If the file size is less than 24 MB, transcribe it directly
    if file_size <= 24 * 1024 * 1024:
        with open(f"{AUDIO_FILE_DIR}/{file_path}", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file, 
                response_format="text"
            )
    else:
        # If the file size is more than 24 MB, chunk it
        for i in range(num_chunks):
            # Extract the chunk
            chunk = audio[i*chunk_size:(i+1)*chunk_size]

            # Save the chunk to a temporary file
            chunk.export(f"{AUDIO_FILE_DIR}/temp_chunk.mp3", format="mp3")

            # Transcribe the chunk
            with open(f"{AUDIO_FILE_DIR}/temp_chunk.mp3", "rb") as audio_file:
                chunk_transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file, 
                    response_format="text",
                    prompt="Respond with ' ' if there are no words present"
                )

            # Append the chunk transcript to the overall transcript
            transcript += chunk_transcript

    return transcript

