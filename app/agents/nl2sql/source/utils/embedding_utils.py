import openai
import numpy as np
import logging
   
def compute_embedding(text: str) -> np.array:
        try:
            response = openai.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response
        
        except Exception as e:
            logging.error("Error computing embedding: %s", e)
            raise



        
