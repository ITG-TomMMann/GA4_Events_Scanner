"""
Main application entry point for the JLR RAG API.
"""
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import routers
from app.agents.doc_rag.api.routes import router as doc_rag_router
from app.agents.nl2sql.routers.ga4_router import router as ga4_router
from app.agents.nl2sql.routers.nl2sql_router import router as nl2sql_router

# Import services
from app.agents.doc_rag.config.settings import get_settings
from app.agents.doc_rag.utils.doc_embeddings import embedding_service
from app.agents.doc_rag.utils.gcp import gcp_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Initialize services on startup
@app.on_event("startup")
def startup_event():
    """Initialize services on application startup."""
    logger.info("Starting JLR RAG API...")
    try:
        # Initialize embedding service
        embedding_service.initialize()
        logger.info("Embedding service initialized")
       
        # Initialize GCP service
        gcp_service.initialize()
        logger.info("GCP service initialized")
       
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}", exc_info=True)
        # We don't raise here to allow the app to start even if some services fail

# Include API routers
app.include_router(doc_rag_router, prefix="/api")
app.include_router(ga4_router, prefix="/api")
app.include_router(nl2sql_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "online",
        "available_endpoints": [
            "/api/query",
            "/api/nl2sql/query",
            "/api/ga4"  # Add any other important endpoints here
        ]
    }

# Main entrypoint for running with uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
   
    uvicorn.run(
        "app.agents.doc_rag.main:app",  # Use the full path to the module
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )