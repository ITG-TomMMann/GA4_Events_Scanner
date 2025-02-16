from fastapi import FastAPI
from routes import router
from config import PROJECT_NAME
from utils import log_info

app = FastAPI(title=PROJECT_NAME)

app.include_router(router, prefix="/api", tags=["nl2sql"])

@app.get("/")
def root():
    log_info("Root endpoint accessed.")
    return {"message": "Welcome to the NL2SQL API!"}
