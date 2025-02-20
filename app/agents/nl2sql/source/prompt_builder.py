import logging

def build_prompt(query: str, schema: str, examples: list, extra_context: str = None) -> str:
    """
    Build a dynamic prompt for NL2SQL generation.

    Parameters:
        query (str): The user's natural language query.
        schema (str): The database schema information.
        examples (list): A list of few-shot examples, each as a dict with keys 'nl_query' and 'sql'.
        extra_context (str, optional): Additional context to include in the prompt.

    Returns:
        str: The final prompt, ready for use with a language model.
    """
    prompt = "Database Schema:\n" + schema + "\n\n"
    prompt += "Few-Shot Examples:\n"
    for example in examples:
        prompt += f"NL Query: {example.get('nl_query')}\nSQL: {example.get('sql')}\n\n"
    prompt += "User Query:\n" + query + "\n"
    if extra_context:
        prompt += "\nAdditional Context:\n" + extra_context + "\n"
    logging.debug("Built prompt: %s", prompt)
    return prompt
