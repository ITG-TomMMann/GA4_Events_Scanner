import os
import sqlparse
from typing import Dict
import logging

def parse_user_provided_schema(user_input: str) -> Dict:
    # Implement actual parsing logic here
    return {"user_table": {"columns": ["id", "name", "email"]}}

import os

def fetch_schema_sql() -> str:
    # Determine the absolute path to the 'config' directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(current_dir, "..", "..", "config")
    schema_sql_path = os.path.join(config_dir, "schema.sql")
    schema_sql_path = os.path.normpath(schema_sql_path)
    
    with open(schema_sql_path, "r") as file:
        return file.read()

def infer_schema(schema_sql: str) -> Dict:
    parsed = sqlparse.parse(schema_sql)
    schema = {}
    logging.info("Starting schema inference.")

    try:
        for stmt_index, statement in enumerate(parsed):
            logging.info(f"\nProcessing statement {stmt_index}: {statement}\n")
            
            # Debug: Print all tokens for the current statement
            for token_index, token in enumerate(statement.tokens):
                logging.debug(
                    f"Statement {stmt_index}, Token {token_index}: '{token}' "
                    f"(Type: {type(token)}, ttype: {token.ttype})"
                )
            
            # Only process CREATE statements
            if statement.get_type() == 'CREATE':
                tokens = statement.tokens
                table_name = None
                columns = []
                found_table_keyword = False

                for token_index, token in enumerate(tokens):
                    logging.debug(
                        f"Processing statement {stmt_index}, token {token_index}: '{token}' "
                        f"(Type: {type(token)}, ttype: {token.ttype})"
                    )
                    
                    # Look for the TABLE keyword
                    if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == "TABLE":
                        found_table_keyword = True
                        logging.debug(f"Found 'TABLE' keyword at token {token_index}.")
                    # If we've found TABLE keyword, next Identifier might be the table name
                    elif found_table_keyword and isinstance(token, sqlparse.sql.Identifier):
                        table_name = token.get_real_name()
                        logging.debug(f"Found table name: '{table_name}' at token {token_index}.")
                        found_table_keyword = False  # Reset flag after capturing table name
                    # Process potential columns inside a Parenthesis
                    elif isinstance(token, sqlparse.sql.Parenthesis):
                        # Flatten the tokens inside the parenthesis for easier processing
                        for col_token in token.flatten():
                            # Only proceed if col_token is an Identifier
                            if isinstance(col_token, sqlparse.sql.Identifier):
                                try:
                                    col_name = col_token.get_name()
                                except Exception as e:
                                    logging.debug(f"Token '{col_token}' does not support get_name: {e}")
                                    col_name = None
                                if col_name:
                                    columns.append(col_name)
                                    logging.debug(f"Found column: '{col_name}'.")
                if table_name:
                    schema[table_name] = {"columns": columns}
                    logging.info(f"Schema for table '{table_name}': {columns}")
                else:
                    logging.warning("Table name not found in CREATE statement.")
        logging.info("Schema inference complete.")
    except Exception as e:
        logging.error("Error inferring schema: %s", e)
        raise

    return schema