import os
from dotenv import load_dotenv

def load_config():
    """Load environment variables from a .env file."""
    load_dotenv()  # Load variables from .env file

    config = {
        "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///default.db"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "APP_ENV": os.getenv("APP_ENV", "development")
    }

    return config
