"""Chat endpoints with SSE streaming."""

import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.core.graph import app as langgraph_app

router = APIRouter()


class ChatRequest(BaseModel):
    """Request body for chat endpoints."""
    message: str
    user_id: str = "andy_dev"  # Default user for now


class ChatResponse(BaseModel):
    """Response body for sync chat endpoint."""
    response: str
    intent: str | None = None


async def generate_sse_stream(message: str, user_id: str) -> AsyncGenerator[str, None]:
    """
    Generate SSE stream from LangGraph response.
    Uses the existing LangGraph workflow.
    """
    try:
        from langchain_core.messages import HumanMessage
        
        # Prepare initial state for LangGraph
        # State expects 'messages' as list of BaseMessage
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "debug_logs": [],
            "intent": None,
        }
        
        # Run the graph (sync call wrapped for async)
        result = await asyncio.to_thread(
            langgraph_app.invoke,
            initial_state
        )
        
        # Extract response from the last message
        messages = result.get("messages", [])
        response_text = messages[-1].content if messages else ""
        
        if not response_text:
            yield "data: Lo siento, no pude procesar tu mensaje.\n\n"
            yield "data: [DONE]\n\n"
            return
        
        # Stream response word by word
        words = response_text.split(" ")
        for i, word in enumerate(words):
            if i > 0:
                yield f"data:  {word}\n\n"
            else:
                yield f"data: {word}\n\n"
            await asyncio.sleep(0.02)
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        print(f"[API] Error in SSE stream: {e}")
        import traceback
        traceback.print_exc()
        yield f"data: Error: {str(e)}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Synchronous chat endpoint.
    Waits for full response before returning.
    """
    try:
        from langchain_core.messages import HumanMessage
        
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "debug_logs": [],
            "intent": None,
        }
        
        result = await asyncio.to_thread(
            langgraph_app.invoke,
            initial_state
        )
        
        messages = result.get("messages", [])
        response_text = messages[-1].content if messages else "No response"
        
        return ChatResponse(
            response=response_text,
            intent=result.get("intent")
        )
        
    except Exception as e:
        print(f"[API] Error in chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE streaming chat endpoint.
    Streams response token by token.
    """
    return StreamingResponse(
        generate_sse_stream(request.message, request.user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
