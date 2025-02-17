from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.memory import ChatMessageHistory
from langchain.chains import ConversationalRetrievalChain
from utils.logger import setup_logger
from schema_agent import get_schema
from rag.retrieval import retrieve_examples
from query_agent import generate_sql
from utils.prompt_builder import build_prompt
import yaml
import os
import logging

app = FastAPI()
history = ChatMessageHistory()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Text-to-SQL CLI")
    parser.add_argument('--query', type=str, help="Natural language query")
    parser.add_argument('--schema', type=str, help="Optional schema input")
    return parser.parse_args()


def load_config():
    source_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(source_dir, "..", "config", "config.yaml")
    config_path = os.path.normpath(config_path)

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


# Comment out or remove the existing CLI-based main function
# def main():
#     setup_logger()
#     args = parse_arguments()
#     config = load_config()
#
#     while True:
#         nl_query = args.query if args.query else input("Enter your query (or 'exit' to quit): ")
#         if nl_query.lower() == 'exit':
#             break
#         schema = get_schema(args.schema)
#         examples = retrieve_examples(nl_query)
#         sql = generate_sql(nl_query, schema, examples)
#         print(f"Generated SQL:\n{sql}")
#         args.query = None
#
# if __name__ == "__main__":
#     main()
class QueryRequest(BaseModel):
    query: str
    session_id: str

class FollowUpRequest(BaseModel):
    follow_up_query: str
    session_id: str
@app.post("/query")
def handle_query(request: QueryRequest):
    setup_logger()
    config = load_config()
    try:
        # Retrieve conversation history
        memory = memory_manager.get_memory(request.session_id)
        
        conversation = history.get_messages(request.session_id)
        
        # Get schema
        schema = get_schema()
        
        # Retrieve few-shot examples
        examples = retrieve_examples(request.query)
        
        # Build prompt with history
        prompt = build_prompt(request.query, schema, examples)
        
        # Generate SQL
        sql = generate_sql(request.query, schema, examples)
        
        # Update conversation history
        memory.add_user_message(request.query)
        memory.add_ai_message(sql)
        
        history.add_message(request.session_id, user=request.query, assistant=sql)
        
        return {"session_id": request.session_id, "sql": sql}
    except Exception as e:
        logging.error(f"Error handling query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/followup")
def handle_followup(request: FollowUpRequest):
    setup_logger()
    config = load_config()
    try:
        # Retrieve conversation history
        conversation = history.get_messages(request.session_id)
        
        # Get schema
        schema = get_schema()
        
        # Retrieve few-shot examples based on follow-up query
        examples = retrieve_examples(request.follow_up_query)
        
        # Build prompt with history
        prompt = build_prompt(request.follow_up_query, schema, examples)
        
        # Generate SQL
        sql = generate_sql(request.follow_up_query, schema, examples)
        
        # Update conversation history
        history.add_message(request.session_id, user=request.follow_up_query, assistant=sql)
        
        return {"session_id": request.session_id, "sql": sql}
    except Exception as e:
        logging.error(f"Error handling follow-up query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
from utils.memory_manager import MemoryManager

memory_manager = MemoryManager()
@app.post("/clear_memory")
def clear_session_memory(session_id: str):
    try:
        memory_manager.clear_memory(session_id)
        return {"detail": f"Memory for session {session_id} cleared."}
    except Exception as e:
        logging.error(f"Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
