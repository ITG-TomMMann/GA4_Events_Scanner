import json
from typing import List, Dict

def build_prompt(nl_query: str, schema: dict, examples: List[Dict]) -> str:
    with open('examples/query_prompt_template.txt', 'r') as template_file:
        template = template_file.read()
    
    formatted_schema = json.dumps(schema, indent=2)
    formatted_examples = "\n".join([f"Example {i+1}:\n{ex['nl_query']} => {ex['sql']}" for i, ex in enumerate(examples)])
    
    prompt = template.format(
        natural_language_query=nl_query,
        schema=formatted_schema,
        few_shot_examples=formatted_examples
    )
    return prompt
