import uuid
import logging
import io
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Import the BigQuery service
from app.agents.nl2sql.services.bigquery_service import bq_service, BigQueryService

# Initialize the router
router = APIRouter(
    prefix="/bigquery",
    tags=["bigquery"],
    responses={404: {"description": "Not found"}},
)

# Create a storage for query results
query_results = {}

# Request models
class BigQueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 1000
    project_id: Optional[str] = None

class QueryExecRequest(BaseModel):
    query_id: str
    max_results: Optional[int] = 1000

@router.post("/estimate-cost")
async def estimate_query_cost(request: BigQueryRequest):
    """
    Estimate the cost of a BigQuery SQL query without executing it.
    
    Returns cost information and a query_id that can be used to execute the query.
    """
    try:
        # Generate a unique ID for this query
        query_id = str(uuid.uuid4())
        
        # Store the query for later execution
        query_results[query_id] = {
            "query": request.query,
            "max_results": request.max_results,
            "project_id": request.project_id,
            "status": "cost_estimated",
            "data": None
        }
        
        # Use custom project_id if provided
        if request.project_id:
            custom_bq_service = BigQueryService(project_id=request.project_id)
            cost_estimate = custom_bq_service.estimate_query_cost(request.query)
        else:
            cost_estimate = bq_service.estimate_query_cost(request.query)
        
        # Add query_id to the response
        cost_estimate["query_id"] = query_id
        
        return cost_estimate
    except Exception as e:
        logging.error(f"Error estimating query cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute/{query_id}")
async def execute_stored_query(query_id: str, background_tasks: BackgroundTasks):
    """
    Execute a previously cost-estimated query by its query_id.
    
    The query execution happens in the background. You can check the status
    and download results when ready.
    """
    if query_id not in query_results:
        raise HTTPException(status_code=404, detail="Query ID not found")
    
    query_info = query_results[query_id]
    
    if query_info["status"] not in ["cost_estimated", "failed"]:
        return {
            "query_id": query_id,
            "row_count": 0 if query_info["data"] is None else len(query_info["data"]),
            "message": f"Query already in status: {query_info['status']}"
        }
    
    # Update status
    query_results[query_id]["status"] = "running"
    
    # Define background task to execute query
    def run_query(qid: str):
        try:
            query_info = query_results[qid]
            
            # Use custom project_id if provided
            if query_info["project_id"]:
                custom_bq_service = BigQueryService(project_id=query_info["project_id"])
                df = custom_bq_service.execute_query(
                    query_info["query"], 
                    max_results=query_info["max_results"]
                )
            else:
                df = bq_service.execute_query(
                    query_info["query"], 
                    max_results=query_info["max_results"]
                )
            
            # Store results in memory
            query_results[qid]["data"] = df
            query_results[qid]["status"] = "completed"
            
        except Exception as e:
            logging.error(f"Error executing query {qid}: {e}")
            query_results[qid]["status"] = "failed"
            query_results[qid]["error"] = str(e)
    
    # Start background task
    background_tasks.add_task(run_query, query_id)
    
    return {
        "query_id": query_id,
        "row_count": 0,
        "message": "Query execution started in background"
    }

@router.post("/direct-execute")
async def direct_execute_query(request: BigQueryRequest):
    """
    Execute a BigQuery SQL query and return both cost and results directly.
    
    This is a convenience endpoint that combines cost estimation and execution.
    For large queries, the separate estimate-cost and execute endpoints are recommended.
    """
    try:
        # First estimate the cost
        if request.project_id:
            custom_bq_service = BigQueryService(project_id=request.project_id)
            cost_estimate = custom_bq_service.estimate_query_cost(request.query)
            
            # Execute the query
            df = custom_bq_service.execute_query(
                request.query, 
                max_results=request.max_results
            )
        else:
            cost_estimate = bq_service.estimate_query_cost(request.query)
            
            # Execute the query
            df = bq_service.execute_query(
                request.query, 
                max_results=request.max_results
            )
        
        # Generate a unique ID for this query
        query_id = str(uuid.uuid4())
        
        # Store results
        query_results[query_id] = {
            "query": request.query,
            "max_results": request.max_results,
            "project_id": request.project_id,
            "status": "completed",
            "data": df
        }
        
        # Convert first few rows to json for preview
        preview_data = df.head(10).to_dict(orient="records")
        
        # Return results with download link
        return {
            "cost_estimate": cost_estimate,
            "execution_result": {
                "query_id": query_id,
                "row_count": len(df),
                "preview_data": preview_data,
                "columns": df.columns.tolist(),
                "message": "Query executed successfully"
            },
            "download_url": f"/bigquery/download/{query_id}"
        }
    except Exception as e:
        logging.error(f"Error in direct execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{query_id}")
async def query_status(query_id: str):
    """Check the status of a query by its query_id."""
    if query_id not in query_results:
        raise HTTPException(status_code=404, detail="Query ID not found")
    
    query_info = query_results[query_id]
    status_info = {
        "query_id": query_id,
        "status": query_info["status"],
        "row_count": 0 if query_info["data"] is None else len(query_info["data"]),
    }
    
    # Include error if present
    if "error" in query_info:
        status_info["error"] = query_info["error"]
    
    # Include preview data if available
    if query_info["data"] is not None:
        status_info["preview_data"] = query_info["data"].head(10).to_dict(orient="records")
        status_info["columns"] = query_info["data"].columns.tolist()
    
    return status_info

@router.get("/download/{query_id}")
async def download_csv(query_id: str):
    """
    Download query results as CSV by query_id.
    
    This endpoint streams the results, so it works well for large datasets.
    """
    if query_id not in query_results:
        raise HTTPException(status_code=404, detail="Query ID not found")
    
    query_info = query_results[query_id]
    
    if query_info["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Query not ready for download. Current status: {query_info['status']}"
        )
    
    if query_info["data"] is None:
        raise HTTPException(status_code=500, detail="Query completed but no data available")
    
    # Create an in-memory buffer for CSV
    csv_buffer = io.StringIO()
    query_info["data"].to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    # Convert to bytes for streaming
    csv_bytes = io.BytesIO(csv_buffer.getvalue().encode())
    
    # Create a filename based on query_id
    filename = f"query_results_{query_id}.csv"
    
    return StreamingResponse(
        csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.delete("/cleanup/{query_id}")
async def cleanup_query(query_id: str):
    """Delete stored query results to free up memory."""
    if query_id not in query_results:
        raise HTTPException(status_code=404, detail="Query ID not found")
    
    del query_results[query_id]
    return {"message": f"Query {query_id} has been deleted"}

@router.get("/datasets")
async def list_datasets():
    """List all datasets in the project."""
    try:
        datasets = bq_service.list_datasets()
        return {"datasets": datasets}
    except Exception as e:
        logging.error(f"Error listing datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables/{dataset_id}")
async def list_tables(dataset_id: str):
    """List all tables in a dataset."""
    try:
        tables = bq_service.list_tables(dataset_id)
        return {"tables": tables}
    except Exception as e:
        logging.error(f"Error listing tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schema/{dataset_id}/{table_id}")
async def get_table_schema(dataset_id: str, table_id: str):
    """Get schema for a specific table."""
    try:
        schema = bq_service.get_table_schema(f"{dataset_id}.{table_id}")
        return schema
    except Exception as e:
        logging.error(f"Error getting schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))