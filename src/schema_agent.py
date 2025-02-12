from typing import Optional, Dict
from utils.schema_inference import infer_schema
import logging

def get_schema(user_input: Optional[str] = None) -> Dict:
    if user_input:
        # Optionally handle user-provided pseudo-schema
        schema = parse_user_provided_schema(user_input)
        logging.info("Using user-provided schema.")
    else:
        # Infer schema from SQL definition
        schema_sql = fetch_schema_sql()
        schema = infer_schema(schema_sql)
        logging.info("Inferred schema from SQL.")
    return schema
