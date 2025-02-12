import sqlparse
from typing import Dict
import logging

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
                    if token.ttype is None and token.value.upper().startswith("TABLE"):
                        table_name = token.value.split()[1]
                    elif isinstance(token, sqlparse.sql.Parenthesis):
                        for col_def in token.tokens:
                            if isinstance(col_def, sqlparse.sql.IdentifierList):
                                for identifier in col_def.get_identifiers():
                                    col_name = identifier.get_name()
                                    columns.append(col_name)
                if table_name:
                    schema[table_name] = {"columns": columns}
        logging.info("Schema inference successful.")
    except Exception as e:
        logging.error("Error inferring schema: %s", e)
        raise
    return schema
