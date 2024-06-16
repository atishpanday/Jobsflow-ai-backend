from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_chain import call_chain

import asyncio

server = FastAPI(root_path="/api")

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


def format_message(message: Message):
    if message.role == "user":
        return "human: " + message.content
    else:
        return "ai: " + message.content


@server.post("/chat")
async def respond_to_message(messages: list[Message]):
    num_messages = len(messages)
    question = messages[num_messages - 1].content
    chat_history = ""
    for m in messages[0:-1]:
        chat_history += "\n" + format_message(m)

    return StreamingResponse(
        call_chain(question, chat_history), media_type="application/json"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(server, host="0.0.0.0", port=8000)
