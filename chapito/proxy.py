import json
from typing import Callable, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager

import time
import uuid
from pydantic import BaseModel, field_validator
import uvicorn
import logging

from chapito.config import Config
from pydoll.browser.chromium import Chrome
from pydoll.browser.tab import Tab


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if hasattr(app.state, 'browser') and app.state.browser:
        logging.info("Shutting down browser...")
        await app.state.browser.stop()

async def generate_json_stream(data: dict):
    data["choices"][0]["delta"] = data["choices"][0]["message"]
    del data["choices"][0]["message"]
    yield f"data: {json.dumps(data)}\n\n"
    yield "data: [DONE]\n\n"


class Message(BaseModel):
    role: str
    content: str

    @field_validator("content", mode="before")
    def transform_content(cls, value):
        if isinstance(value, list):
            text_parts = [item["text"] for item in value if item.get("type") == "text"]
            return "\n\n".join(text_parts)
        return value


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


app = FastAPI(lifespan=lifespan)

last_chat_messages: List[str] = []


def find_index_from_end(lst: List[Message], values: List[str]) -> int:
    for i in range(len(lst) - 1, -1, -1):
        message = lst[i]
        if message.content.strip() in values:
            return i
    return -1


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=404, content={"message": "Undefined route", "requested_url": request.url.path})

@app.get("/models")
async def get_models(): 
    return [
        {
            "name": "chapito",
            "type": "chat",
            "censored": True,
            "description": "Chapito",
            "baseModel": True
        }
    ]

@app.post("/chat/completions")
async def chat_completions(request: ChatRequest):
    global last_chat_messages

    logging.debug(f"Request received: {request}")

    if not request.messages:
        raise HTTPException(status_code=400, detail="Field 'messages' is missing or empty")
        
    last_revelant_message_position = -2 if len(request.messages) >= 2 else -1
    if len(request.messages) > 0:
        logging.debug(f"Last relevant message in request: {request.messages[last_revelant_message_position]}")

    index_of_last_message = find_index_from_end(request.messages, last_chat_messages)
    prompt = "\n\n".join(
        f"[{message.role}] {message.content}" for message in request.messages[index_of_last_message + 1 :]
    )
    last_chat_messages.append(request.messages[-1].content.strip())
    if not prompt:
        logging.debug("Can't determine latest messages, sending the whole chat session")
        prompt = "\n\n".join(f"[{message.role}] {message.content}" for message in request.messages)

    response_content = await app.state.send_request_and_get_response(app.state.tab, prompt)
    if response_content:
        last_chat_messages.append(response_content)
    logging.debug(f"Response from chat ends with: {response_content[-100:]}")
    logging.debug("Sending response")

    data = {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response_content, "refusal": None},
                "finish_reason": "stop",
                # "logprobs": {"content": [], "refusal": []},
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(response_content.split()),
            "total_tokens": len(prompt.split()) + len(response_content.split()),
            "cost": 0,
        },
    }
    if app.state.config.stream:
        logging.debug("Send StreamingResponse")
        return StreamingResponse(generate_json_stream(data), media_type="text/event-stream")
    else:
        logging.debug("Send JSONResponse")
        return JSONResponse(data)


def init_proxy(browser: Chrome, tab: Tab, send_request_and_get_response: Callable, config: Config) -> None:
    app.state.browser = browser
    app.state.tab = tab
    app.state.send_request_and_get_response = send_request_and_get_response
    app.state.config = config

    logging.debug(f"Listening on: {config.host}:{config.port}")

    uvicorn.run(app, host=config.host, port=config.port)
