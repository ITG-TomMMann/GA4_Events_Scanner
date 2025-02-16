import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_info(message: str):
    """
    Log an informational message using Python's logging.
    """
    logger.info(message)

def clean_text(text: str) -> str:
    """
    Perform basic text normalization.
    """
    return text.strip().lower()
