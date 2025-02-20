import os
import json
import logging

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Use an absolute import assuming the project root is 'nl2sql'
from app.agents.nl2sql.source.utils.file_reader import read_markdown

# Build the path to RoutePrompt.md located in the 'prompts' folder at the project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_FILE_PATH = os.path.join(CURRENT_DIR, "..", "prompts", "RoutePrompt.md")

def get_routing_prompt() -> str:
    """
    Reads and returns the routing prompt from the RoutePrompt.md file.
    
    Returns:
        str: The content of the RoutePrompt.md file.
    """
    try:
        return read_markdown(PROMPT_FILE_PATH)
    except Exception as e:
        logging.error(f"Error reading routing prompt: {e}", exc_info=True)
        raise

def classify_question(query: str) -> dict:
    """
    Classify the input query as either SIMPLE or COMPLEX using a language model.
    
    Parameters:
        query (str): The natural language query to classify.
    
    Returns:
        dict: A dictionary with the classification result, e.g., {"choice": "SIMPLE"}.
    """
    try:
        # Load the routing prompt from the markdown file
        routing_prompt = get_routing_prompt()

        # Create a prompt template using the loaded markdown content
        prompt_template = PromptTemplate(
            input_variables=["question"],
            template=routing_prompt
        )
        
        # Initialize the LLM (using OpenAI as an example)
        llm = OpenAI(temperature=0)
        
        # Create an LLM chain with the prompt template
        llm_chain = LLMChain(llm=llm, prompt=prompt_template)
        
        # Run the chain to get the classification response
        response = llm_chain.run(query)
        
        # Parse the response as JSON
        classification = json.loads(response.strip())
        return classification

    except Exception as e:
        logging.error(f"Error classifying question: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Test the classifier with an example query
    test_query = "What is the CTR of this new component on this page?"
    result = classify_question(test_query)
    print("Classification result:", result)
