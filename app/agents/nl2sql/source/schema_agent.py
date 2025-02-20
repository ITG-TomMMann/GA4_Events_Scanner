import os
from .utils.table_selector import TableSelector
from typing import Optional, Dict
from .utils.schema_inference import infer_schema, parse_user_provided_schema, fetch_schema_sql
import logging

# Determine the absolute path to the 'config' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(current_dir, "..", "config")
schema_sql_path = os.path.join(config_dir, "schema.sql")
schema_sql_path = os.path.normpath(schema_sql_path)
print(schema_sql_path)

# Initialize TableSelector with the absolute path
table_selector = TableSelector(schema_sql_path=schema_sql_path)

def get_schema(user_input: Optional[str] = None, query: str = "") -> Dict:
    if user_input:
        # Handle user-provided pseudo-schema
        schema = parse_user_provided_schema(user_input)
        logging.info("Using user-provided schema.")
    else:
        # Infer schema from SQL definition
        schema_sql = fetch_schema_sql()
        schema = infer_schema(schema_sql)
        logging.info("Inferred schema from SQL.")
    # Optimize table selection based on query context
    relevant_tables = table_selector.select_relevant_tables(query)
    optimized_schema = {table: schema[table] for table in relevant_tables if table in schema}
    return optimized_schema
import sqlparse
from typing import Dict
import logging

def validate_sql(sql_query: str, schema: Dict) -> bool:
    try:
        parsed = sqlparse.parse(sql_query)
        for statement in parsed:
            if statement.get_type() != 'SELECT':
                logging.warning("Only SELECT statements are allowed.")
                return False
            # Basic validation: check table and column names
            tokens = [token for token in statement.tokens if not token.is_whitespace]
            from_seen = False
            for token in tokens:
                if from_seen:
                    if isinstance(token, sqlparse.sql.Identifier):
                        table_name = token.get_real_name()
                        if table_name not in schema:
                            logging.warning(f"Table {table_name} not found in schema.")
                            return False
                if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                    from_seen = True
            # Additional validation can be added here
        logging.info("SQL validation successful.")
        return True
    except Exception as e:
        logging.error(f"Error validating SQL: {e}")
        return False
