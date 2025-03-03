import uuid
import logging
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlparse

from langchain.memory import ConversationBufferMemory

# Example placeholders for your own imports
from .utils.logger import setup_logger
from .schema_agent import get_schema
from .rag.retrieval import retrieve_examples
from .query_agent import generate_sql
from .utils.prompt_builder import build_prompt
from .query_classifier import classify_query_complexity
from .complex_sql_generator import generate_complex_sql

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware


origins = [
    "https://storage.googleapis.com",  # Cloud Storage base
    "https://storage.googleapis.com/ai-data-analyst-static-site",  # Your frontend
    "https://*.storage.googleapis.com",  # Wildcard for any subpath
    "http://localhost:5173",  # Local dev
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Explicitly define origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


###############################################################################
# 1. Memory Manager that returns a ConversationBufferMemory per session
###############################################################################
class MemoryManager:
    def __init__(self):
        self.memories = {}

    def get_memory(self, session_id: str) -> ConversationBufferMemory:
        if session_id in self.memories:
            return self.memories[session_id]
        else:
            memory = ConversationBufferMemory(memory_key="history")
            self.memories[session_id] = memory
            return memory

    def clear_memory(self, session_id: str):
        if session_id in self.memories:
            del self.memories[session_id]


memory_manager = MemoryManager()

###############################################################################
# 2. Request Models
###############################################################################
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None  # Optional, so we can auto-generate

class FollowUpRequest(BaseModel):
    follow_up_query: str
    session_id: str  # For follow-ups, we assume session_id is known

class ClearMemoryRequest(BaseModel):  # Fix for session_id passing
    session_id: str

from fastapi import Request

@app.options("/{full_path:path}")
async def preflight_handler(full_path: str, request: Request):
    return {}


###############################################################################
# 3. Main Endpoints
###############################################################################
@app.post("/query")
def handle_query(request: QueryRequest):
    try:
        setup_logger()

        # 1) Determine or generate session_id
        session_id = request.session_id or str(uuid.uuid4())

        # 2) Retrieve or create the ConversationBufferMemory for this session
        memory = memory_manager.get_memory(session_id)

        # 3) Classification step

        # 4) Shared steps: retrieve schema and examples
        schema = get_schema()
        examples = retrieve_examples(request.query)

        # 5) Add user’s message to memory
        memory.chat_memory.add_user_message(request.query)

        # 6) Branch logic based on classification

        complexity = classify_query_complexity(request.query, examples)
        
        # Step 2: Generate SQL based on complexity
        if complexity == "SIMPLE":
            sql = generate_sql(request.query, schema, examples)
        else:
            sql = generate_complex_sql(request.query, schema, examples)


        formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')


        # 7) Add the AI response (SQL) to memory
        memory.chat_memory.add_ai_message(formatted_sql)

        # 8) Return session_id and response
        return {"session_id": session_id, "sql": formatted_sql}

    except Exception as e:
        logging.error(f"Error handling query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/followup")
def handle_followup(request: FollowUpRequest):
    try:
        # Ensure logger is set up
        setup_logger()

        # Get existing memory for this session
        memory = memory_manager.get_memory(request.session_id)

        # Inspect conversation history
        conversation_list = memory.chat_memory.messages

        # Add the user’s follow-up message
        memory.chat_memory.add_user_message(request.follow_up_query)

        # Generate AI’s follow-up response
        schema = get_schema()
        examples = retrieve_examples(request.follow_up_query)
        prompt = build_prompt(request.follow_up_query, schema, examples)
        sql = generate_sql(request.follow_up_query, schema, examples)

        formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')

        # Add AI response
        memory.chat_memory.add_ai_message(formatted_sql)

        # Return session_id and response
        return {"session_id": request.session_id, "sql": formatted_sql}

    except Exception as e:
        logging.error(f"Error handling follow-up: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear_memory")
def clear_session_memory(request: ClearMemoryRequest):
    try:
        memory_manager.clear_memory(request.session_id)
        return {"detail": f"Memory for session {request.session_id} cleared."}
    except Exception as e:
        logging.error(f"Error clearing memory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

###############################################################################
# 4. Run the App (Dev)
###############################################################################
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
