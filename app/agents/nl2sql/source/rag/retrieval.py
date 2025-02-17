import numpy as np
from rag.vector_store import VectorStore
from utils.embedding_utils import compute_embedding
import json
import logging
import os 
from pathlib import Path



def retrieve_examples(nl_query: str, top_n: int = 5) -> list:
    # (Your embedding computation and vector store code goes here...)
    embedding_response = compute_embedding(nl_query)
    embedding = compute_embedding(nl_query)
    
    vector_store = VectorStore(dimension=embedding.shape[0], index_path="rag/vector_store.faiss")
    distances, indices = vector_store.index.search(np.array([embedding]), top_n)

    # Build the path to examples.json by going up one level from "source" to "nl2sql", then into "examples"
    examples_path = nl2sql_dir.parent  / "examples" / "examples.json"
    print("Looking for examples.json at:", examples_path)  # For debugging

    with open(examples_path, 'r') as f:
        examples = json.load(f)
    
    retrieved = [examples[i] for i in indices[0] if i < len(examples)]
    logging.info("Retrieved %d examples.", len(retrieved))
    return retrieved
