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

    def add_vectors(self, vectors: np.array):
        self.index.add(vectors)
        logging.info("Added %d vectors to FAISS index.", len(vectors))

    def save_index(self):
        faiss.write_index(self.index, self.index_path)
        logging.info("FAISS index saved to %s.", self.index_path)

    def load_index(self):
        self.index = faiss.read_index(self.index_path)
