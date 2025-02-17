from langchain.prompts import PromptTemplate
import os
import json
from typing import List, Dict

def build_prompt(nl_query: str, schema: dict, examples: List[Dict]) -> str:
    try:
        # Define the prompt template using LangChain's PromptTemplate
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

        formatted_schema = json.dumps(schema, indent=2)
        formatted_examples = "\n\n".join([
            f"Example {i+1}:\nNL Query: {ex['nl_query']}\nSQL Query: {ex['sql']}"
            for i, ex in enumerate(examples)
        ])

        final_prompt = prompt.format(
            schema=formatted_schema,
            few_shot_examples=formatted_examples,
            natural_language_query=nl_query
        )
        return final_prompt
    except Exception as e:
        logging.error(f"Error building prompt: {e}")
        raise
