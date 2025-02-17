import faiss
import numpy as np
import os
import logging

class VectorStore:
    def __init__(self, dimension: int, index_path: str):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.index_path = index_path
        if os.path.exists(index_path):
            self.load_index()
            logging.info("FAISS index loaded.")
        else:
            logging.info("Initialized new FAISS index.")
