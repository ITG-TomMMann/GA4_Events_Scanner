import os
import sqlparse
from typing import Dict
import logging

def parse_user_provided_schema(user_input: str) -> Dict:
    # Implement actual parsing logic here
    return {"user_table": {"columns": ["id", "name", "email"]}}

def fetch_schema_sql() -> str:
    # Implement logic to fetch schema from a database or file
    with open("config/schema.sql", "r") as file:
        return file.read()

def infer_schema(schema_sql: str) -> Dict:
    parsed = sqlparse.parse(schema_sql)
    schema = {}
    try:
        for statement in parsed:
            if statement.get_type() == 'CREATE':
                tokens = statement.tokens
                table_name = None
                columns = []
                for token in tokens:
                    if isinstance(token, sqlparse.sql.Identifier) and token.value.upper().startswith("TABLE"):
                        table_name = token.get_real_name()
                        logging.debug(f"Found table: {table_name}")
                    elif isinstance(token, sqlparse.sql.Parenthesis):
                        for col_def in token.tokens:
                            if isinstance(col_def, sqlparse.sql.IdentifierList):
                                for identifier in col_def.get_identifiers():
                                    if isinstance(identifier, sqlparse.sql.Identifier):
                                        col_name = identifier.get_name()
                                        if col_name:
                                            columns.append(col_name)
                                            logging.debug(f"Found column: {col_name}")
                                    else:
                                        logging.debug(f"Skipping non-Identifier token: {identifier}")
                if table_name:
                    schema[table_name] = {"columns": columns}
                    logging.info(f"Schema for table '{table_name}': {columns}")
                else:
                    logging.warning("Table name not found in CREATE statement.")
        logging.info("Schema inference successful.")
    except Exception as e:
        logging.error("Error inferring schema: %s", e)
        raise
    return schema
