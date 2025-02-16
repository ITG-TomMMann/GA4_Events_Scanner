from fastapi import APIRouter, HTTPException
from models import NL2SQLRequest, NL2SQLResponse
from openai_service import generate_response
from utils import log_info, clean_text

router = APIRouter()

@router.post("/nl2sql", response_model=NL2SQLResponse)
def create_sql_from_nl(request: NL2SQLRequest):
    """
    Convert a natural language query into a SQL statement using OpenAI.
    """
    try:
        cleaned_query = clean_text(request.query_text)
        log_info(f"Received query: {cleaned_query}")
        prompt = f"Convert this user query into a SQL statement: {cleaned_query}"
        sql_query = generate_response(prompt)
        log_info(f"Generated SQL query: {sql_query}")
        return NL2SQLResponse(sql_query=sql_query, status="ok", results=[])
    except Exception as e:
        log_info(f"Error in /nl2sql endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
