from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from .utils.embedding_utils import compute_embedding
import json
import logging
import os

def retrieve_examples(nl_query: str, top_n: int = 5) -> list:
    try:
        # Load few-shot examples
        with open('examples/examples.json', 'r') as f:
            examples = json.load(f)
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create or load FAISS index
        if os.path.exists("rag/vector_store.faiss"):
            vector_store = FAISS.load_local("rag/vector_store.faiss", embeddings)
            logging.info("FAISS index loaded.")
        else:
            vector_store = FAISS.from_documents(examples, embeddings)
            vector_store.save_local("rag/vector_store.faiss")
            logging.info("FAISS index created and saved.")
        
        # Retrieve top-N similar examples
        query_embedding = embeddings.embed_query(nl_query)
        docs = vector_store.similarity_search_by_vector(query_embedding, k=top_n)
        
        retrieved = [doc.page_content for doc in docs]
        logging.info(f"Retrieved {len(retrieved)} examples.")
        return retrieved
    except Exception as e:
        logging.error(f"Error retrieving examples: {e}")
        raise
