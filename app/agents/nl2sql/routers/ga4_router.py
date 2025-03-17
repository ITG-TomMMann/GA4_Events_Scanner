from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union

from app.agents.nl2sql.services.ga4_service import process_ga4_request


# Define router
router = APIRouter(
    prefix="/api",
    tags=["ga4"],
    responses={404: {"description": "Not found"}},
)

# Request model
class GA4RequestModel(BaseModel):
    url: str

# Response model
class GA4ResponseModel(BaseModel):
    response: Union[List[Dict[str, Any]], Dict[str, Any]]

@router.post("/ga4", response_model=GA4ResponseModel)
async def ga4_endpoint(message: GA4RequestModel):
    """
    Endpoint to collect GA4 events from a URL.
    
    Args:
        message: Request object containing the URL to analyze
        
    Returns:
        GA4ResponseModel: Response containing parsed GA4 events or error message
    """
    result = process_ga4_request(message.url)
    
    # Check if there was an error
    if isinstance(result, dict) and "error" in result:
        return GA4ResponseModel(response=result)
    
    return GA4ResponseModel(response=result)