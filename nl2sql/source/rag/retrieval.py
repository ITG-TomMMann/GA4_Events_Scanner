import numpy as np
from rag.vector_store import VectorStore
from utils.embedding_utils import compute_embedding
import json
import logging

def retrieve_examples(nl_query: str, top_n: int = 5) -> list:
    embedding_response = compute_embedding(nl_query)
    # Extract the actual embedding array
    embedding = np.array(embedding_response.data[0].embedding)
    vector_store = VectorStore(dimension=embedding.shape[0], index_path='rag/vector_store.faiss')
    distances, indices = vector_store.index.search(np.array([embedding]), top_n)
    
    with open('nl2sql/examples/examples.json', 'r') as f:
        examples = json.load(f)
    
    retrieved = [examples[i] for i in indices[0] if i < len(examples)]
    logging.info("Retrieved %d examples.", len(retrieved))
    return retrieved
