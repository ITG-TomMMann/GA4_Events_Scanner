import uuid
import logging
from typing import Optional, List, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlparse
import json
import os
import numpy as np
import datetime
from .utils.db_manager import db_manager

from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate

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
    "https://storage.googleapis.com/ai-data-analyst-static-site",  # Your frontend
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
        self.previous_analyses = {}  # Store previous analyses by query hash

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
    
    def store_analysis(self, query_key: str, sql: str, results: Dict = None):
        """Store an analysis for future reference"""
        self.previous_analyses[query_key] = {
            "sql": sql,
            "results": results,
            "timestamp":  datetime.datetime.now().isoformat()
        }
    
    def get_analysis(self, query_key: str) -> Dict:
        """Retrieve a previous analysis if it exists"""
        return self.previous_analyses.get(query_key)


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
# 3. Intent Classification Function
###############################################################################
def classify_intent(query: str) -> str:
    """
    Classifies the intent of a user query as one of:
    - analytical: Requires SQL generation for data analysis
    - informational: General questions about capabilities, how-to, etc.
    - conversational: Casual conversation, greetings, etc.
    - existing_analysis: Checking for already performed analysis
    
    Args:
        query (str): The user's query text
        
    Returns:
        str: The classified intent
    """
    try:
        prompt = PromptTemplate(
            input_variables=["query"],
            template="""Classify the intent of the following query into exactly one of these categories:
            - analytical: Requires SQL or data analysis (e.g., "Show me sales data", "Count users by country")
            - informational: Questions about how the tool works, capabilities (e.g., "What can you do?", "How do I use this?")
            - conversational: General chat, greetings (e.g., "How are you?", "Hello")
            - existing_analysis: Asking about previous analysis (e.g., "Did we analyze this before?", "Show me the previous report on user engagement")

            Query: {query}
            
            Respond with exactly one word (the category name):"""
        )
        
        llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        chain = prompt | llm | StrOutputParser()
        intent = chain.invoke({"query": query}).strip().lower()
        
        # Validate the intent is one of our expected categories
        valid_intents = ["analytical", "informational", "conversational", "existing_analysis"]
        if intent not in valid_intents:
            logging.warning(f"Invalid intent classification: {intent}. Defaulting to analytical.")
            intent = "analytical"
            
        logging.info(f"Query intent classified as: {intent}")
        return intent
        
    except Exception as e:
        logging.error(f"Error classifying intent: {e}")
        # Default to analytical in case of errors
        return "analytical"


###############################################################################
# 4. Check for Previous Similar Analysis
###############################################################################
def find_similar_analysis(query: str) -> Dict:
    """
    Check if we've done a similar analysis before by using embeddings similarity
    
    Args:
        query (str): The current query
        
    Returns:
        Dict or None: Previous analysis if found, otherwise None
    """
    try:
        from langchain_openai import OpenAIEmbeddings
        
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        query_embedding = embeddings.embed_query(query)
        
        # Find the most similar previous analysis
        best_match = None
        highest_similarity = 0.8  # Threshold for similarity
        
        
        
        for prev_query, analysis in memory_manager.previous_analyses.items():
            # Get embedding for the previous query
            prev_embedding = embeddings.embed_query(prev_query)
            
            # Calculate similarity
            similarity = cosine_similarity(
                np.array(query_embedding).reshape(1, -1),
                np.array(prev_embedding).reshape(1, -1)
            )[0][0]
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = analysis
        
        return best_match
    except Exception as e:
        logging.error(f"Error finding similar analysis: {e}")
        return None


###############################################################################
# 5. Handle Non-Analytical Queries
###############################################################################
def handle_non_analytical_query(query: str, intent: str) -> str:
    """
    Generate appropriate responses for non-analytical queries
    
    Args:
        query (str): The user's query
        intent (str): The classified intent
        
    Returns:
        str: Response to the user
    """
    try:
        prompt = PromptTemplate(
            input_variables=["query", "intent"],
            template="""You are an AI assistant specialized in data analytics and SQL generation. 
            
            The user has asked a question that has been classified as {intent} rather than requiring data analysis.
            
            User query: {query}
            
            Please respond appropriately:
            - If it's an informational query, explain your capabilities related to SQL generation and data analysis
            - If it's a conversational query, respond in a friendly, brief manner and guide them toward analytical questions
            
            Keep your response concise and helpful:"""
        )
        
        llm = ChatOpenAI(
            model="gpt-4", 
            temperature=0.7,  # Slightly higher temperature for more natural responses
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"query": query, "intent": intent})
        
        return response
        
    except Exception as e:
        logging.error(f"Error handling non-analytical query: {e}")
        return "I'm an AI assistant that helps with data analysis through SQL queries. How can I help you analyze your data?"


###############################################################################
# 6. Main Endpoints
###############################################################################
@app.post("/query")
def handle_query(request: QueryRequest):
    try:
        setup_logger()

        # 1) Determine or generate session_id
        session_id = request.session_id or str(uuid.uuid4())

        # 2) Retrieve or create the ConversationBufferMemory for this session
        memory = memory_manager.get_memory(session_id)

        # 3) Add user's message to memory
        memory.chat_memory.add_user_message(request.query)
        
        # 4) NEW: Classify the intent of the query
        db_manager.store_message(
            session_id=session_id,
            message_type="user",
            content=request.query
        )
        
        # 4) Classify the intent of the query
        intent = classify_intent(request.query)
        
        # 5) Branch logic based on intent classification
        if intent == "analytical":
            # Standard analytical workflow
            schema = get_schema()
            examples = retrieve_examples(request.query)
            
            # Check query complexity for SQL generation approach
            complexity = classify_query_complexity(request.query, examples)
            
            # Generate SQL based on complexity
            if complexity == "SIMPLE":
                sql = generate_sql(request.query, schema, examples)
            else:
                sql = generate_complex_sql(request.query, schema, examples)
                
            # Format SQL for readability
            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
            
            # Store assistant message in database
            db_manager.store_message(
                session_id=session_id,
                message_type="assistant",
                content=formatted_sql,
                query_type="analytical",
                sql_query=formatted_sql
            )
            
            # Store SQL query for later retrieval
            db_manager.store_sql_query(
                session_id=session_id,
                natural_language_query=request.query,
                sql_query=formatted_sql,
                complexity=complexity
            )
            
            # Add the AI response (SQL) to memory
            memory.chat_memory.add_ai_message(formatted_sql)
            
            # Return session_id and SQL
            return {"session_id": session_id, "sql": formatted_sql, "type": "sql"}
            
        elif intent == "existing_analysis":
            # Check for exact match using hash
            import hashlib
            query_hash = hashlib.md5(request.query.encode()).hexdigest()
            exact_match = db_manager.get_sql_query_by_hash(query_hash)
            
            if exact_match:
                response = f"I found a previous analysis for this query. Here's the SQL query that was used:\n\n{exact_match['sql_query']}"
                
                # Store assistant message in database
                db_manager.store_message(
                    session_id=session_id,
                    message_type="assistant",
                    content=response,
                    query_type="existing_analysis",
                    sql_query=exact_match['sql_query']
                )
                
                memory.chat_memory.add_ai_message(response)
                return {
                    "session_id": session_id, 
                    "message": response, 
                    "sql": exact_match['sql_query'], 
                    "type": "existing_analysis"
                }
            
            # If no exact match, generate a new SQL query
            schema = get_schema()
            examples = retrieve_examples(request.query)
            complexity = classify_query_complexity(request.query, examples)
            
            if complexity == "SIMPLE":
                sql = generate_sql(request.query, schema, examples)
            else:
                sql = generate_complex_sql(request.query, schema, examples)
                
            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
            
            # Store assistant message in database
            db_manager.store_message(
                session_id=session_id,
                message_type="assistant",
                content=formatted_sql,
                query_type="analytical",
                sql_query=formatted_sql
            )
            
            # Store SQL query for later retrieval
            db_manager.store_sql_query(
                session_id=session_id,
                natural_language_query=request.query,
                sql_query=formatted_sql,
                complexity=complexity
            )
            
            memory.chat_memory.add_ai_message(formatted_sql)
            return {
                "session_id": session_id, 
                "sql": formatted_sql, 
                "type": "sql", 
                "message": "I didn't find any previous analyses for this query, so I've generated a new SQL query for you."
            }
        
        else:  # Handle informational or conversational intents
            response = handle_non_analytical_query(request.query, intent)
            
            # Store assistant message in database
            db_manager.store_message(
                session_id=session_id,
                message_type="assistant",
                content=response,
                query_type=intent
            )
            
            memory.chat_memory.add_ai_message(response)
            return {"session_id": session_id, "message": response, "type": "conversation"}

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

        # Add the user's follow-up message
        memory.chat_memory.add_user_message(request.follow_up_query)
        
        # Store user message in database
        db_manager.store_message(
            session_id=request.session_id,
            message_type="user",
            content=request.follow_up_query
        )
        
        # Classify the intent of the follow-up query
        intent = classify_intent(request.follow_up_query)
        
        if intent in ["informational", "conversational"]:
            response = handle_non_analytical_query(request.follow_up_query, intent)
            
            # Store assistant message in database
            db_manager.store_message(
                session_id=request.session_id,
                message_type="assistant",
                content=response,
                query_type=intent
            )
            
            memory.chat_memory.add_ai_message(response)
            return {"session_id": request.session_id, "message": response, "type": "conversation"}
        else:
            # Generate AI's follow-up response for analytical queries
            schema = get_schema()
            examples = retrieve_examples(request.follow_up_query)
            complexity = classify_query_complexity(request.follow_up_query, examples)
            
            if complexity == "SIMPLE":
                sql = generate_sql(request.follow_up_query, schema, examples)
            else:
                sql = generate_complex_sql(request.follow_up_query, schema, examples)

            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
            
            # Store assistant message in database
            db_manager.store_message(
                session_id=request.session_id,
                message_type="assistant",
                content=formatted_sql,
                query_type="analytical",
                sql_query=formatted_sql
            )
            
            # Store SQL query for later retrieval
            db_manager.store_sql_query(
                session_id=request.session_id,
                natural_language_query=request.follow_up_query,
                sql_query=formatted_sql,
                complexity=complexity
            )
            
            # Add AI response
            memory.chat_memory.add_ai_message(formatted_sql)

            # Return session_id and response
            return {"session_id": request.session_id, "sql": formatted_sql, "type": "sql"}

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
# 7. Run the App (Dev)
###############################################################################
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)