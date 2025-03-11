import uuid
import logging
from typing import Optional, List, Dict
import os

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlparse
import json

# Import the BigQuery router
from app.agents.nl2sql.routers.bigquery_router import router as bq_router

# Import BigQuery service for use in main app logic
from app.agents.nl2sql.services.bigquery_service import bq_service, BigQueryService


# Original imports
try:
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
    from .utils.db_manager import db_manager
except ImportError:
    # Create stubs for missing modules in development/testing
    logging.warning("Some modules could not be imported. Using stub implementations for testing.")
    
    def setup_logger():
        logging.basicConfig(level=logging.INFO)
    
    def get_schema():
        return "stub_schema"
    
    def retrieve_examples(query):
        return ["SELECT * FROM users LIMIT 10"]
    
    def generate_sql(query, schema, examples):
        return f"-- Generated SQL for: {query}\nSELECT * FROM sample_table LIMIT 10"
    
    def build_prompt(query, schema, examples):
        return f"Generate SQL for: {query}"
    
    def classify_query_complexity(query, examples):
        return "SIMPLE"
    
    def generate_complex_sql(query, schema, examples):
        return f"-- Complex SQL for: {query}\nSELECT * FROM sample_table JOIN other_table USING(id) LIMIT 10"
    
    class DBManager:
        def store_message(self, **kwargs):
            logging.info(f"Storing message: {kwargs}")
        
        def store_sql_query(self, **kwargs):
            logging.info(f"Storing SQL query: {kwargs}")
        
        def get_sql_query_by_hash(self, query_hash):
            return None
    
    db_manager = DBManager()

app = FastAPI(
    title="AI SQL Generator with BigQuery Support",
    description="API for generating SQL from natural language and executing queries via BigQuery",
    version="1.0.0"
)

# Add CORS middleware
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

# Include the BigQuery router
app.include_router(bq_router)

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
            "timestamp": json.dumps({"date": str(datetime.datetime.now())})
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
    execute_query: Optional[bool] = False  # Whether to execute the query via BigQuery
    max_results: Optional[int] = 1000  # Maximum number of results to return

class FollowUpRequest(BaseModel):
    follow_up_query: str
    session_id: str  # For follow-ups, we assume session_id is known
    execute_query: Optional[bool] = False  # Whether to execute the query via BigQuery
    max_results: Optional[int] = 1000  # Maximum number of results to return

class ClearMemoryRequest(BaseModel):  # Fix for session_id passing
    session_id: str

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
# 4. Handle Non-Analytical Queries
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
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("OpenAI API key not found in environment variables")
            return "I'm experiencing configuration issues. Please ensure the OpenAI API key is properly configured."
        
        logging.info(f"Handling non-analytical query: '{query}' with intent: {intent}")
        
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
        
        logging.info("Initializing ChatOpenAI")
        llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0.7,  # Slightly higher temperature for more natural responses
            openai_api_key=api_key
        )
        
        logging.info("Building and invoking LangChain pipeline")
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"query": query, "intent": intent})
        
        logging.info(f"Generated response (first 100 chars): {response[:100]}...")
        
        if not response or response.strip() == "":
            logging.warning("Empty response received from language model")
            return "I'm an AI assistant that helps with data analysis through SQL queries. How can I help you analyze your data?"
        
        return response
        
    except Exception as e:
        logging.error(f"Error handling non-analytical query: {e}", exc_info=True)
        return "I'm an AI assistant that helps with data analysis through SQL queries. How can I help you analyze your data?"


###############################################################################
# 5. Main Endpoints
###############################################################################
@app.post("/query")
def handle_query(request: QueryRequest, background_tasks: BackgroundTasks):
    try:
        setup_logger()

        # 1) Determine or generate session_id
        session_id = request.session_id or str(uuid.uuid4())

        # 2) Retrieve or create the ConversationBufferMemory for this session
        memory = memory_manager.get_memory(session_id)

        # 3) Add user's message to memory
        memory.chat_memory.add_user_message(request.query)
        
        # 4) Store user message in database
        db_manager.store_message(
            session_id=session_id,
            message_type="user",
            content=request.query
        )
        
        # 5) Classify the intent of the query
        intent = classify_intent(request.query)
        logging.info(f"Query classified as: {intent}")
        
        # 6) Branch logic based on intent classification
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
            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='UPPER')
            
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
            
            # If execute_query is True, run the query in BigQuery
            if request.execute_query:
                # Add BigQuery execution logic here (omitted for brevity)
                pass
            
            # Return session_id and SQL without execution - CONSISTENT RESPONSE FORMAT
            return {
                "session_id": session_id, 
                "sql": formatted_sql, 
                "message": "Here's the SQL query to answer your question:", 
                "type": "sql"
            }
            
        elif intent == "existing_analysis":
            # Check for exact match using hash
            import hashlib
            query_hash = hashlib.md5(request.query.encode()).hexdigest()
            exact_match = db_manager.get_sql_query_by_hash(query_hash)
            
            if exact_match:
                response_message = f"I found a previous analysis for this query. Here's the SQL query that was used:"
                
                # Store assistant message in database
                db_manager.store_message(
                    session_id=session_id,
                    message_type="assistant",
                    content=response_message,
                    query_type="existing_analysis",
                    sql_query=exact_match['sql_query']
                )
                
                memory.chat_memory.add_ai_message(response_message)
                
                # Return with CONSISTENT RESPONSE FORMAT
                return {
                    "session_id": session_id, 
                    "message": response_message, 
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
                
            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='UPPER')
            
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
            
            # Return with CONSISTENT RESPONSE FORMAT
            return {
                "session_id": session_id, 
                "sql": formatted_sql, 
                "message": "I didn't find any previous analyses for this query, so I've generated a new SQL query for you.", 
                "type": "sql"
            }
        
        else:  # Handle informational or conversational intents
            # Get response for non-analytical query
            response = handle_non_analytical_query(request.query, intent)
            logging.info(f"Non-analytical response: {response[:100]}...")
            
            # Store assistant message in database
            db_manager.store_message(
                session_id=session_id,
                message_type="assistant",
                content=response,
                query_type=intent
            )
            
            memory.chat_memory.add_ai_message(response)
            
            # Return with CONSISTENT RESPONSE FORMAT - Always include both message and sql fields
            return {
                "session_id": session_id, 
                "message": response, 
                "sql": None,  # Explicitly including SQL as None for non-SQL responses
                "type": "conversation"
            }

    except Exception as e:
        logging.error(f"Error handling query: {e}", exc_info=True)
        # Even error responses should maintain consistent format
        return {
            "session_id": request.session_id or str(uuid.uuid4()),
            "message": f"Error processing your request: {str(e)}",
            "sql": None,
            "type": "error",
            "error": str(e)
        }


@app.post("/followup")
def handle_followup(request: FollowUpRequest, background_tasks: BackgroundTasks):
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
        logging.info(f"Follow-up query classified as: {intent}")
        
        if intent in ["informational", "conversational"]:
            # Handle non-analytical query
            response = handle_non_analytical_query(request.follow_up_query, intent)
            logging.info(f"Generated non-analytical response: {response[:100]}...")
            
            # Store assistant message in database
            db_manager.store_message(
                session_id=request.session_id,
                message_type="assistant",
                content=response,
                query_type=intent
            )
            
            memory.chat_memory.add_ai_message(response)
            
            # Return with CONSISTENT RESPONSE FORMAT
            return {
                "session_id": request.session_id, 
                "message": response, 
                "sql": None,  # Explicitly include SQL as None
                "type": "conversation"
            }
        else:
            # Generate AI's follow-up response for analytical queries
            schema = get_schema()
            examples = retrieve_examples(request.follow_up_query)
            complexity = classify_query_complexity(request.follow_up_query, examples)
            
            if complexity == "SIMPLE":
                sql = generate_sql(request.follow_up_query, schema, examples)
            else:
                sql = generate_complex_sql(request.follow_up_query, schema, examples)

            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='UPPER')
            
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

            # If execute_query is True, run the query in BigQuery
            if request.execute_query:
                # Add BigQuery execution logic here (omitted for brevity)
                pass

            # Return session_id and response with CONSISTENT RESPONSE FORMAT
            return {
                "session_id": request.session_id, 
                "sql": formatted_sql, 
                "message": "Here's the SQL query for your follow-up question:", 
                "type": "sql"
            }

    except Exception as e:
        logging.error(f"Error handling follow-up: {e}", exc_info=True)
        # Even error responses should maintain consistent format
        return {
            "session_id": request.session_id,
            "message": f"Error processing your follow-up request: {str(e)}",
            "sql": None,
            "type": "error",
            "error": str(e)
        }


@app.post("/clear_memory")
def clear_session_memory(request: ClearMemoryRequest):
    try:
        memory_manager.clear_memory(request.session_id)
        return {"detail": f"Memory for session {request.session_id} cleared."}
    except Exception as e:
        logging.error(f"Error clearing memory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


###############################################################################
# 6. Run the App (Dev)
###############################################################################
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)