import os
import json
from typing import List, Dict

def build_prompt(nl_query: str, schema: dict, examples: List[Dict]) -> str:
    # Get the absolute path of the current file (located in "source")
    source_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to "nl2sql"
    nl2sql_dir = os.path.abspath(os.path.join(source_dir, ".."))
    nl2sql_dir_2 = os.path.abspath(os.path.join(nl2sql_dir, ".."))
    # Then into the "examples/quer_prompt" folder
    template_path = os.path.join(nl2sql_dir_2, "examples",  "query_prompt_template.txt")
    
    with open(template_path, 'r') as template_file:
        template = template_file.read()
    
    formatted_schema = json.dumps(schema, indent=2)
    formatted_examples = "\n".join([
        f"Example {i+1}:\n{ex['nl_query']} => {ex['sql']}" 
        for i, ex in enumerate(examples)
    ])
    
    prompt = template.format(
        natural_language_query=nl_query,
        schema=formatted_schema,
        few_shot_examples=formatted_examples
    )
    return prompt
