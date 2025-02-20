from langchain.prompts import PromptTemplate
import os
import json
import logging
from typing import List, Dict

def build_prompt(nl_query: str, schema: dict, examples: List[Dict]) -> str:
    try:
        if not examples or not isinstance(examples, list):
            logging.error("Examples are missing or incorrectly formatted.")
            raise ValueError("Invalid examples format.")

        # Validate that each example is a dictionary
        formatted_examples = "\n\n".join([
            f"Example {i+1}:\nNL Query: {ex.get('nl_query', 'MISSING')}\nSQL Query: {ex.get('sql', 'MISSING')}"
            for i, ex in enumerate(examples) if isinstance(ex, dict)
        ])
        
        template = """You are an AI assistant that converts natural language queries into SQL statements.
        
        Schema:
        {schema}

        Few-shot Examples:
        {few_shot_examples}

        Natural Language Query:
        {natural_language_query}

        SQL Query:"""

        prompt = PromptTemplate(
            input_variables=["schema", "few_shot_examples", "natural_language_query"],
            template=template
        )

        final_prompt = prompt.format(
            schema=json.dumps(schema, indent=2),
            few_shot_examples=formatted_examples,
            natural_language_query=nl_query
        )

        logging.info(f"Generated prompt: {final_prompt}")
        return final_prompt

    except Exception as e:
        logging.error(f"Error in `build_prompt`: {e}", exc_info=True)
        raise

