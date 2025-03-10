from typing import Dict
import logging

class ConversationHandler:
    """Handles non-analytical queries like capability questions and general conversation"""
    
    def __init__(self):
        self.capabilities = {
            "sql_generation": "I can convert natural language questions into SQL queries",
            "data_analysis": "I can analyze data from your database using SQL",
            "conversation": "I can maintain context in our conversation",
        }

    def handle_general_query(self, query: str) -> Dict[str, str]:
        """Handle general queries about capabilities, development plans etc."""
        
        if "capabilities" in query.lower() or "what can you do" in query.lower():
            response = "I can help you with:\n"
            for capability, description in self.capabilities.items():
                response += f"- {description}\n"
            return {"type": "conversation", "response": response}
            
        elif "development plan" in query.lower():
            response = ("I'm continuously being developed to improve my capabilities. "
                      "Current development plans include enhancing SQL generation accuracy, "
                      "adding more complex query support, and improving conversation context handling.")
            return {"type": "conversation", "response": response}
            
        else:
            response = ("I'm primarily designed to help with data analysis queries. "
                      "Could you please rephrase your question in terms of data analysis?")
            return {"type": "conversation", "response": response}
