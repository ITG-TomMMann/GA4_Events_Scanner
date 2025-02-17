import openai
import numpy as np
import logging
   
def compute_embedding(text: str) -> np.array:
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            embedding = np.array(response['data'][0]['embedding'])
            return embedding
        except Exception as e:
            logging.error("Error computing embedding: %s", e)
            raise



        
