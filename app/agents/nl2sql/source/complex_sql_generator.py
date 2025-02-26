import os
import logging
import json
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate

def generate_complex_sql(nl_query: str, schema: dict, few_shot_examples: list) -> str:
    """
    Generate SQL for complex queries using a more powerful model with specific prompting.
    
    Args:
        nl_query (str): The natural language query
        schema (dict): Database schema information
        few_shot_examples (list): Example queries with their SQL
        
    Returns:
        str: Generated SQL query
    """
    try:
        # Ensure prompt has required inputs
        if not schema or not few_shot_examples:
            raise ValueError("Schema or examples missing")

        # Format schema
        formatted_schema = json.dumps(schema, indent=2)

        # Filter for complex examples if available
        complex_examples = [ex for ex in few_shot_examples if ex.get('complexity') == 'complex']
        examples_to_use = complex_examples if complex_examples else few_shot_examples[:2]
        
        # Format examples
        formatted_examples = "\n\n".join([
            f"Example {i+1}:\nNL Query: {ex.get('nl_query', '')}\nSQL Query: {ex.get('sql', '')}"
            for i, ex in enumerate(examples_to_use)
        ])

        prompt = PromptTemplate(
            input_variables=["schema", "few_shot_examples", "natural_language_query"],
            template="""You are an expert SQL developer specializing in writing optimized, complex SQL queries. Your task is to convert natural language queries into advanced SQL.

            For complex queries, you should:
            1. Use Common Table Expressions (CTEs) to break down complex logic into manageable parts
            2. Apply window functions where appropriate for analytics
            3. Structure hierarchical data queries with recursive CTEs when needed
            4. Use appropriate subqueries and joins
            5. Consider performance by limiting data early in the query pipeline
            6. Add helpful comments to explain complex logic
            
            Format the SQL query according to industry standard best practices (e.g., use uppercase for SQL keywords, proper indentation, and consistent spacing).

            Schema:
            {schema}

            Complex Query Examples:
            {few_shot_examples}

            Natural Language Query:
            {natural_language_query}

            SQL Query:"""
        )

        # Use GPT-4 for complex queries
        llm = ChatOpenAI(
            model="gpt-4", 
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Create chain
        chain = prompt | llm | StrOutputParser()

        # Generate SQL
        sql_query = chain.invoke({
            "schema": formatted_schema,
            "few_shot_examples": formatted_examples,
            "natural_language_query": nl_query
        })

        logging.info(f"Generated Complex SQL Query: {sql_query}")

        return sql_query

    except Exception as e:
        logging.error(f"Error generating complex SQL: {e}")
        raise