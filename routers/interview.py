from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydub import AudioSegment
import io
import wave
from utils.speech_to_text import DG_Client
from dotenv import load_dotenv
import os
import asyncio

load_dotenv(".env.local")

router = APIRouter()


@router.websocket("/interview")
async def handle_interview(websocket: WebSocket):
    await websocket.accept()
    connection_open = True
    audio_data = bytearray()
    dg_client = DG_Client(os.getenv("DG_API_KEY"))
    dg_client.connect()
    try:
        while connection_open:
            data = await websocket.receive_bytes()
            audio_data.extend(data)
            dg_client.add_audio(data)
    except WebSocketDisconnect:
        print("Client disconnected")
        connection_open = False
    except Exception as e:
        print(f"Error: {e}")
        connection_open = False
    finally:
        if connection_open:
            await websocket.close()
            connection_open = False

    # Decode WebM audio data
    webm_audio = io.BytesIO(audio_data)
    audio = AudioSegment.from_file(webm_audio, format="webm")

    # Save as WAV
    wav_audio = io.BytesIO()
    audio.export(wav_audio, format="wav")

    # Write the WAV data to a file
    with wave.open("received_audio.wav", "wb") as audio_file:
        audio_file.setnchannels(audio.channels)
        audio_file.setsampwidth(audio.sample_width)
        audio_file.setframerate(audio.frame_rate)
        audio_file.writeframes(wav_audio.getbuffer())
