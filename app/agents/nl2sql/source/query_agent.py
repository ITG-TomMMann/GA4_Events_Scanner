from langchain.prompts import PromptTemplate
import os
import logging
from langchain_community.chat_models import ChatOpenAI  # Fix deprecated import
from langchain.schema.runnable import RunnableLambda
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
import json

def generate_sql(nl_query: str, schema: dict, few_shot_examples: list) -> str:
    try:
        # Ensure prompt has required inputs
        if not schema or not few_shot_examples:
            raise ValueError("Schema or examples missing")

        # Construct a valid schema string
        formatted_schema = json.dumps(schema, indent=2)

        # Construct few-shot examples
        formatted_examples = "\n\n".join([
            f"Example {i+1}:\nNL Query: {ex['nl_query']}\nSQL Query: {ex['sql']}"
            for i, ex in enumerate(few_shot_examples)
        ])

        prompt = PromptTemplate(
            input_variables=["schema", "few_shot_examples", "natural_language_query"],
            template="""You are an AI assistant that converts natural language queries into SQL statements.

            Please format the SQL query according to industry standard best practices (e.g., use uppercase for SQL keywords, proper indentation, and consistent spacing).
            Before outputting make sure the query is formatted like so: 

            SELECT 
                COUNT(DISTINCT visitor_id) AS total_visitors
            FROM 
                `jlr-dl-dxa.PRD_GA4.GA4_hit`
            WHERE 
                page_path LIKE '%range-rover/nameplate/index.html';

            

            Schema:
            {schema}

            Few-shot Examples:
            {few_shot_examples}

            Natural Language Query:
            {natural_language_query}

            SQL Query:"""
        )

        # Use the latest ChatOpenAI import
        llm = ChatOpenAI(model="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))

        # New LangChain recommended approach
        chain = prompt | llm | StrOutputParser()

        # Invoke chain with correct parameters
        sql_query = chain.invoke({
            "schema": formatted_schema,
            "few_shot_examples": formatted_examples,
            "natural_language_query": nl_query
        })

        logging.info(f"Generated SQL Query: {sql_query}")

        return sql_query

    except Exception as e:
        logging.error(f"Error generating SQL: {e}")
        raise
