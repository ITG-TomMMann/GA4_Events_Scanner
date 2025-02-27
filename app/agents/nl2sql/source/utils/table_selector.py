import json
import os
import logging
from typing import List, Dict

class TableSelector:
    def __init__(self, schema_json_path: str):
        self.schema_json_path = schema_json_path
        self.schema = self._load_schema()
        
    def _load_schema(self) -> Dict:
        """Load the JSON schema file"""
        try:
            if os.path.exists(self.schema_json_path):
                with open(self.schema_json_path, 'r') as f:
                    return json.load(f)
            else:
                logging.warning(f"Schema file not found: {self.schema_json_path}")
                return {}
        except Exception as e:
            logging.error(f"Error loading schema: {e}")
            return {}
            
    def select_relevant_tables(self, query: str) -> List[str]:
        """Select tables that are relevant to the query"""
        if not query:
            # Return all tables if no query provided
            if "tables" in self.schema:
                return list(self.schema["tables"].keys())
            return list(self.schema.keys())
            
        # Extract tables based on keywords in the query
        tables = []
        
        # Get all available tables
        if "tables" in self.schema:
            available_tables = self.schema["tables"]
        else:
            available_tables = self.schema
            
        # Simple keyword matching (can be enhanced with NLP/embeddings)
        for table_name, table_info in available_tables.items():
            # Check if table name appears in query
            if table_name.lower() in query.lower():
                tables.append(table_name)
                
            # Check if table description appears in query
            if "description" in table_info and table_info["description"].lower() in query.lower():
                tables.append(table_name)
                
            # Check if any column name appears in query
            if "columns" in table_info:
                for column_name in table_info["columns"].keys():
                    if column_name.lower() in query.lower():
                        tables.append(table_name)
                        break
        
        # Ensure we're returning unique tables
        unique_tables = list(set(tables))
        
        # If no tables matched, return all tables
        if not unique_tables:
            return list(available_tables.keys())
            
        return unique_tables