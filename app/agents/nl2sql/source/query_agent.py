import openai
import logging
from typing import List, Dict
from utils.prompt_builder import build_prompt
from openai import OpenAI
import openai
import logging
from typing import List, Dict
from utils.prompt_builder import build_prompt
from schema_agent import validate_sql
from langchain.llms import OpenAI
from langchain.chains import LLMChain

def generate_sql(nl_query: str, schema: dict, few_shot_examples: List[Dict]) -> str:
    try:
        prompt = build_prompt(nl_query, schema, few_shot_examples)
        
        # Initialize LangChain LLM
        llm = OpenAI(model_name="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY"))
        chain = LLMChain(llm=llm, prompt=PromptTemplate(template=prompt, input_variables=[]))
        
        sql_query = chain.run()
        logging.info(f"Generated SQL Query: {sql_query}")
        
        # Validate SQL against schema
        if validate_sql(sql_query, schema):
            return sql_query
        else:
            logging.error("Generated SQL does not comply with the schema.")
            raise ValueError("SQL Validation Failed.")
    except Exception as e:
        logging.error(f"Error generating SQL: {e}")
        raise

