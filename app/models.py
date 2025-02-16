from pydantic import BaseModel
from typing import Optional, List

class NL2SQLRequest(BaseModel):
    """
    Represents a user request for converting a natural language query into SQL.
    """
    query_text: str

class NL2SQLResponse(BaseModel):
    """
    Represents the structured response containing the generated SQL query.
    """
    sql_query: str
    status: str = "ok"
    results: Optional[List[dict]] = None
