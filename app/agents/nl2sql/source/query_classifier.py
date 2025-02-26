import os
import logging
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate

def classify_query_complexity(nl_query: str, examples: list) -> str:
    """
    Classify a query as 'SIMPLE' or 'COMPLEX' based on its characteristics.
    
    Args:
        nl_query (str): The natural language query to classify
        examples (list): List of example queries with complexity labels
    
    Returns:
        str: 'SIMPLE' or 'COMPLEX'
    """
    try:
        # Format examples for the classifier
        formatted_examples = "\n".join([
            f"- Query: \"{ex.get('nl_query', '')}\" -> {ex.get('complexity', 'SIMPLE').upper()}"
            for ex in examples if 'complexity' in ex
        ])

        prompt = PromptTemplate(
            input_variables=["examples", "query"],
            template="""You are a query classifier that determines whether a natural language query should be classified as SIMPLE or COMPLEX for SQL generation.

            Classification criteria:
            - SIMPLE: Basic queries involving straightforward filtering, counting, or aggregation on one or two tables with simple conditions
            - COMPLEX: Queries requiring CTEs, multiple subqueries, window functions, complex joins across multiple tables, or complex analytical operations

            Example classifications:
            {examples}

            Query to classify: "{query}"

            Respond with exactly one word: either SIMPLE or COMPLEX
            """
        )

        # Use a smaller model for classification to save costs
        llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Create the chain
        chain = prompt | llm | StrOutputParser()

        # Get classification
        classification = chain.invoke({
            "examples": formatted_examples,
            "query": nl_query
        }).strip().upper()

        # Validate result
        if classification not in ["SIMPLE", "COMPLEX"]:
            logging.warning(f"Invalid classification result: {classification}. Defaulting to SIMPLE.")
            classification = "SIMPLE"

        logging.info(f"Query classified as: {classification}")
        return classification

    except Exception as e:
        logging.error(f"Error classifying query: {e}")
        # Default to simple in case of errors
        return "SIMPLE"