import openai
import logging
from typing import List, Dict
from utils.prompt_builder import build_prompt

def generate_sql(nl_query: str, schema: dict, few_shot_examples: List[Dict]) -> str:
    prompt = build_prompt(nl_query, schema, few_shot_examples)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        sql_query = response.choices[0].message['content'].strip()
        logging.info("Generated SQL Query: %s", sql_query)
        return sql_query
    except Exception as e:
        logging.error("Error generating SQL: %s", e)
        raise
