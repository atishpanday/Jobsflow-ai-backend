from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.dg_client import DG_Client
from utils.ai_interviewer import AI_Interviewer
from dotenv import load_dotenv
import os
import asyncio
import time

load_dotenv(".env.local")

router = APIRouter()


@router.websocket("/interview")
async def handle_interview(websocket: WebSocket):
    await websocket.accept()
    connection_open = True
    dg_client = DG_Client(os.getenv("DG_API_KEY"))
    dg_client.connect()
    ai_interviewer = AI_Interviewer()
    try:
        while connection_open:
            data = await websocket.receive_bytes()
            dg_client.add_audio(data)
            if len(dg_client.transcription) > 0:
                ai_interviewer.append_to_prompt(dg_client.transcription)
                await websocket.send_text(dg_client.transcription)
                dg_client.reset_transcription()
            s_t = time.time()
            while len(dg_client.transcription) == 0 and len(ai_interviewer.prompt) > 0:
                e_t = time.time()
                if (e_t - s_t) >= 3:
                    await websocket.send_text(
                        f"AI Interviewer: {ai_interviewer.get_response()}"
                    )
                    ai_interviewer.reset_prompt()
                    break
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
