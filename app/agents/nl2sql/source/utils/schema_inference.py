import os
import json
from .table_selector import TableSelector
from typing import Optional, Dict
import logging

# Determine the absolute path to the 'config' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(current_dir, "..", "config")
schema_json_path = os.path.join(config_dir, "schema.json")  # Changed to JSON
schema_json_path = os.path.normpath(schema_json_path)
print(schema_json_path)

# Initialize TableSelector with the absolute path (you'll need to update TableSelector class)
table_selector = TableSelector(schema_json_path=schema_json_path)

def fetch_schema_json():
    """Fetch schema from JSON file"""
    try:
        with open(schema_json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading schema JSON: {e}")
        return {}

def parse_user_provided_schema(user_input: str) -> Dict:
    """Parse user-provided schema in JSON format"""
    try:
        schema = json.loads(user_input)
        return schema
    except json.JSONDecodeError:
        logging.warning("Invalid JSON schema provided by user. Falling back to default schema.")
        return fetch_schema_json()

def get_schema(user_input: Optional[str] = None, query: str = "") -> Dict:
    if user_input:
        # Handle user-provided schema in JSON format
        schema = parse_user_provided_schema(user_input)
        logging.info("Using user-provided schema.")
    else:
        # Load schema from JSON file
        schema = fetch_schema_json()
        logging.info("Loaded schema from JSON file.")
    
    # Extract tables from the schema
    if "tables" in schema:
        tables_dict = schema["tables"]
    else:
        tables_dict = schema  # Fallback if the schema is a direct table mapping
    
    # Optimize table selection based on query context
    relevant_tables = table_selector.select_relevant_tables(query)
    optimized_schema = {table: tables_dict[table] for table in relevant_tables if table in tables_dict}
    
    # Include metrics if they exist in the schema
    if "metrics" in schema:
        optimized_schema["metrics"] = schema["metrics"]
    
    # Include relationships if they exist in the schema
    if "relationships" in schema:
        optimized_schema["relationships"] = schema["relationships"]
        
    return optimized_schema

def validate_sql(sql_query: str, schema: Dict) -> bool:
    """Validate SQL query against JSON schema"""
    try:
        import sqlparse
        parsed = sqlparse.parse(sql_query)
        
        # Extract table names from schema
        if "tables" in schema:
            valid_tables = schema["tables"].keys()
        else:
            valid_tables = schema.keys()  # Fallback
            
        for statement in parsed:
            if statement.get_type() != 'SELECT':
                logging.warning("Only SELECT statements are allowed.")
                return False
                
            # Basic validation: check table names
            tokens = [token for token in statement.tokens if not token.is_whitespace]
            from_seen = False
            for token in tokens:
                if from_seen:
                    if isinstance(token, sqlparse.sql.Identifier):
                        table_name = token.get_real_name()
                        if table_name not in valid_tables:
                            logging.warning(f"Table {table_name} not found in schema.")
                            return False
                if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                    from_seen = True
                    
        logging.info("SQL validation successful.")
        return True
    except Exception as e:
        logging.error(f"Error validating SQL: {e}")
        return False