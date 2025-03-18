from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union

from app.agents.nl2sql.services.ga4_service import process_ga4_request

# Update your FastAPI models and endpoint

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import asyncio

# Update or verify your request model has the correct field
class GA4RequestModel(BaseModel):
    url: str  # Make sure this matches what your React app is sending

class GA4ResponseModel(BaseModel):
    response: dict  # This will contain the GA4 events or error message

# Assuming you have an implementation that uses the GA4EventCollector from the Streamlit code
async def process_ga4_request(url: str) -> dict:
    """Process a URL to extract GA4 events using the GA4EventCollector"""
    try:
        collector = GA4EventCollector()
        events = collector.collect_events_from_url(url, wait_time=5, section_selector="body", target_text=None)
        parsed_ga4_events = [parse_ga4_event(event) for event in collector.ga4_events]
        collector.close()
        return {"events": parsed_ga4_events}
    except Exception as e:
        return {"error": str(e)}

router = APIRouter()

@router.post("/ga4", response_model=GA4ResponseModel)
async def ga4_endpoint(request: GA4RequestModel):
    """
    Endpoint to collect GA4 events from a URL.
    
    Args:
        request: Request object containing the URL to analyze
        
    Returns:
        GA4ResponseModel: Response containing parsed GA4 events or error message
    """
    try:
        # Add a timeout to prevent the request from hanging indefinitely
        result = await asyncio.wait_for(process_ga4_request(request.url), timeout=60)
        return GA4ResponseModel(response=result)
    except asyncio.TimeoutError:
        return GA4ResponseModel(response={"error": "Request timed out after 60 seconds"})
    except Exception as e:
        return GA4ResponseModel(response={"error": f"An unexpected error occurred: {str(e)}"})