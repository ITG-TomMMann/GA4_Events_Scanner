from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from ..utils.embedding_utils import compute_embedding
import json
import logging
import os

def retrieve_examples(nl_query: str, top_n: int = 5) -> list:
    try:
        # Load few-shot examples from JSON
        with open('examples/examples.json', 'r') as f:
            examples = json.load(f)

        # Transform examples into Document instances with 'page_content'
        documents = [
            Document(page_content=f"{ex['nl_query']} => {ex['sql']}")
            for ex in examples
        ]
        
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

        # Create or load FAISS index
        if os.path.exists("rag/vector_store.faiss"):
            vector_store = FAISS.load_local("rag/vector_store.faiss", embeddings, allow_dangerous_deserialization=True)
            logging.info("FAISS index loaded.")
        else:
            vector_store = FAISS.from_documents(documents, embeddings)
            vector_store.save_local("rag/vector_store.faiss")
            logging.info("FAISS index created and saved.")

        # Retrieve top-N similar examples
        query_embedding = embeddings.embed_query(nl_query)
        docs = vector_store.similarity_search_by_vector(query_embedding, k=top_n)

        # Convert retrieved examples back into dictionary format
        retrieved = []
        for doc in docs:
            if "=>" in doc.page_content:
                nl_query, sql = doc.page_content.split("=>", 1)
                retrieved.append({"nl_query": nl_query.strip(), "sql": sql.strip()})
            else:
                logging.warning(f"Malformed FAISS example: {doc.page_content}")

        logging.info(f"Retrieved {len(retrieved)} structured examples.")
        return retrieved

    except Exception as e:
        logging.error(f"Error retrieving examples: {e}", exc_info=True)
        raise
