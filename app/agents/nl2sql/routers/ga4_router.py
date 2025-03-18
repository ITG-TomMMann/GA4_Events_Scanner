from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.agents.nl2sql.services.ga4_service import process_ga4_request
# Define the request and response models
class GA4RequestModel(BaseModel):
    url: str  # This should match what the frontend sends

class GA4ResponseModel(BaseModel):
    response: dict  # This will contain the GA4 events or error message

# Create a thread pool executor for running the Selenium-based code
executor = ThreadPoolExecutor(max_workers=2)  # Limit concurrent Selenium browsers

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
        # Run the Selenium code in a separate thread to not block the event loop
        loop = asyncio.get_event_loop()
        # Execute the function with a timeout
        result = await asyncio.wait_for(
            loop.run_in_executor(executor, process_ga4_request, request.url),
            timeout=90  # 90 seconds timeout
        )
        
        # Process the result based on the format returned by process_ga4_request
        if isinstance(result, list):
            # If we got a list of events, format it for the response
            return GA4ResponseModel(response={"events": result})
        elif isinstance(result, dict):
            # If we got a dict (probably an error), return it as is
            return GA4ResponseModel(response=result)
        else:
            # Unexpected result format
            return GA4ResponseModel(response={"error": "Unexpected response format from processor"})
            
    except asyncio.TimeoutError:
        return GA4ResponseModel(response={"error": "Request timed out. GA4 collection can take time on complex pages."})
    except Exception as e:
        return GA4ResponseModel(response={"error": f"An unexpected error occurred: {str(e)}"})