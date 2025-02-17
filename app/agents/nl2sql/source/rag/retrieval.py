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
    embedding = np.array(embedding_response.data[0].embedding)
    
    # Build the vector store path if needed (example):
    source_dir = Path(__file__).resolve().parent  # This is the "source" folder
    nl2sql_dir = source_dir.parent              # Go up to the "nl2sql" folder
    vector_store_path = nl2sql_dir / "rag" / "vector_store.faiss"
    
    vector_store = VectorStore(dimension=embedding.shape[0], index_path=str(vector_store_path))
    distances, indices = vector_store.index.search(np.array([embedding]), top_n)

    # Build the path to examples.json by going up one level from "source" to "nl2sql", then into "examples"
    examples_path = nl2sql_dir.parent  / "examples" / "examples.json"
    print("Looking for examples.json at:", examples_path)  # For debugging

    with open(examples_path, 'r') as f:
        examples = json.load(f)
    
    retrieved = [examples[i] for i in indices[0] if i < len(examples)]
    logging.info("Retrieved %d examples.", len(retrieved))
    return retrieved