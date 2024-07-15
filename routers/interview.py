from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.dg_client import DG_Client
from utils.ai_interviewer import AI_Interviewer
from dotenv import load_dotenv
import os
import asyncio
import time

load_dotenv(".env.local")

router = APIRouter()

interviewer_questions = [
    "Can you tell me something about yourself?",
    "Why did you apply for this job?",
    "What kind of work experience do you have?",
    "Why should we hire you (and not someone else)?",
]


@router.websocket("/interview")
async def handle_interview(websocket: WebSocket):
    await websocket.accept()
    connection_open = True
    dg_client = DG_Client(os.getenv("DG_API_KEY"))
    dg_client.connect()
    current_transcription = "User:"
    q_num = 0
    try:
        while connection_open:
            data = await websocket.receive_bytes()
            dg_client.add_audio(data)
            if len(dg_client.transcription) > 0:
                current_transcription += dg_client.transcription
                await websocket.send_text(current_transcription)
                dg_client.reset_transcription()
            s_t = time.time()
            while (
                len(dg_client.transcription) == 0
                and len(current_transcription.split(":")[1]) > 0
                and q_num < len(interviewer_questions)
            ):
                e_t = time.time()
                if (e_t - s_t) >= 3:
                    await websocket.send_text(
                        f"Interviewer: {interviewer_questions[q_num]}"
                    )
                    current_transcription = "User:"
                    q_num += 1
        await websocket.send_text(
            "Interviewer: The interview is now complete. Thank you!"
        )
        await websocket.close()
        connection_open = False
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
